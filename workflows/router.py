"""
router.py - LlamaIndex Router: semantic RAG או שליפה מובנית מ-JSON
"""
import json
from pathlib import Path
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine, CustomQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.llms import LLM

STRUCTURED_JSON_PATH = Path(__file__).resolve().parent.parent / "extraction" / "structured_project_data.json"

SCHEMA_DESCRIPTION = """
הנתונים המובנים מכילים שלושה סוגי פריטים:
- decisions: החלטות טכניות (שדות: id, title, source.tool, source.file)
- rules: כללים והנחיות (שדות: id, title, source.tool, source.file)
- warnings: אזהרות (שדות: id, title, source.tool, source.file)

כל פריט שייך לכלי (tool): "cursor" או "claude".
"""


class StructuredQueryEngine(CustomQueryEngine):
    """מנוע שליפה מובנית: LLM בונה פילטר → שולף מ-JSON → LLM מכין תשובה."""
    llm: LLM
    structured_data: dict

    def custom_query(self, query_str: str):
        raise NotImplementedError("use acustom_query")

    async def acustom_query(self, query_str: str):
        # שלב 1: LLM בונה שאילתת JSON לפי הסכמה
        filter_prompt = f"""
אתה מערכת שליפת נתונים. בהתאם לסכמה הבאה:
{SCHEMA_DESCRIPTION}

המשתמש שאל: "{query_str}"

החזר JSON בלבד (ללא הסברים) עם השדות הבאים:
{{
  "category": "decisions" | "rules" | "warnings" | "all",
  "tool_filter": "cursor" | "claude" | null,
  "operation": "count" | "list" | "search",
  "search_term": "<מילת חיפוש אם רלוונטי, אחרת null>"
}}
"""
        filter_response = await self.llm.acomplete(filter_prompt)
        try:
            raw = filter_response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            query_plan = json.loads(raw.strip())
        except Exception:
            return "לא הצלחתי לפרסר את תוכנית השאילתה."

        # שלב 2: שליפה מה-JSON לפי התוכנית
        items_db = self.structured_data.get("items", {})
        category = query_plan.get("category", "all")
        tool_filter = query_plan.get("tool_filter")
        operation = query_plan.get("operation", "list")
        search_term = query_plan.get("search_term")

        categories = ["decisions", "rules", "warnings"] if category == "all" else [category]
        results = []
        for cat in categories:
            items = items_db.get(cat, [])
            if tool_filter:
                items = [i for i in items if (i.get("source") or {}).get("tool") == tool_filter]
            if search_term:
                term = search_term.lower()
                items = [i for i in items if term in (i.get("title") or i.get("rule") or i.get("message") or "").lower()]
            for item in items:
                results.append({"category": cat, **item})

        if operation == "count":
            raw_data = f"נמצאו {len(results)} פריטים."
        elif not results:
            raw_data = "לא נמצאו פריטים התואמים את השאילתה."
        else:
            lines = []
            for r in results:
                text = r.get("title") or r.get("rule") or r.get("message") or ""
                lines.append(f"[{r['category']}][{r.get('id','?')}] {text}")
            raw_data = "\n".join(lines)

        # שלב 3: LLM מכין תשובה סופית
        answer_prompt = f"""
המשתמש שאל: "{query_str}"

תוצאות השליפה מהנתונים המובנים:
{raw_data}

ענה למשתמש בצורה ברורה ותמציתית בהתבסס על התוצאות בלבד.
"""
        final = await self.llm.acomplete(answer_prompt)
        return str(final.text)


class _RAGEngine(CustomQueryEngine):
    """עוטף את ה-RAGWorkflow - async בלבד כי WorkflowHandler דורש running loop."""
    workflow: object

    def custom_query(self, query_str: str):
        raise NotImplementedError("use acustom_query")

    async def acustom_query(self, query_str: str):
        print(f"🔍 [Semantic RAG] מריץ חיפוש סמנטי על: '{query_str}'")
        handler = self.workflow.run(query=query_str)
        result = await handler
        print("✅ [Semantic RAG] התקבלה תשובה")
        return result.answer


def build_router(rag_workflow, llm, embed_model) -> RouterQueryEngine:
    """בונה RouterQueryEngine עם שני כלים: semantic ו-structured."""

    if not STRUCTURED_JSON_PATH.exists():
        raise FileNotFoundError(f"לא נמצא: {STRUCTURED_JSON_PATH}")

    with open(STRUCTURED_JSON_PATH, encoding="utf-8") as f:
        structured_data = json.load(f)

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
