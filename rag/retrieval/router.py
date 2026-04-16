import json
import logging
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine, CustomQueryEngine
from llama_index.core.selectors import LLMSingleSelector

from rag.retrieval.structured_engine import StructuredQueryEngine, STRUCTURED_JSON_PATH


class _RAGEngine(CustomQueryEngine):
    """עוטף את ה-RAGWorkflow - async בלבד כי WorkflowHandler דורש running loop."""
    workflow: object

    def custom_query(self, query_str: str):
        raise NotImplementedError("use acustom_query")

    async def acustom_query(self, query_str: str):
        result = await self.workflow.run(query=query_str)
        return result.answer


def build_router(rag_workflow, llm, embed_model) -> RouterQueryEngine:
    if not STRUCTURED_JSON_PATH.exists():
        raise FileNotFoundError(f"לא נמצא: {STRUCTURED_JSON_PATH}")

    with open(STRUCTURED_JSON_PATH, encoding="utf-8") as f:
        structured_data = json.load(f)
    logging.getLogger(__name__).info("Loaded structured JSON from %s: %d top-level keys", STRUCTURED_JSON_PATH, len(structured_data.keys()))

    tools = [
        QueryEngineTool.from_defaults(
            query_engine=_RAGEngine(workflow=rag_workflow),
            name="semantic_search",
            description=(
                "מתאים לשאלות פתוחות שדורשות הבנה והסבר: 'איך עובד X', 'מה הארכיטקטורה', "
                "'הסבר לי את תהליך Y'. לא מתאים לשאלות שמבקשות רשימה, ספירה, או שליפה של פריטים ספציפיים."
            ),
        ),
        QueryEngineTool.from_defaults(
            query_engine=StructuredQueryEngine(llm=llm, structured_data=structured_data),
            name="structured_data",
            description=(
                "מתאים לכל שאלה שמבקשת: רשימה של פריטים, ספירה ('כמה'), החלטות טכניות, "
                "כללים, אזהרות, חיפוש לפי ID, סינון לפי כלי (cursor/claude), "
                "'מה תיעד X', 'אילו דברים', 'תן לי את כל ה-', 'מה קשור ל-frontend/backend/auth'."
            ),
        ),
    ]

    return RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(llm=llm),
        query_engine_tools=tools,
        verbose=True,
    )
