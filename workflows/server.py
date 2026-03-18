import os
import uuid
from llama_index.core.workflow import Workflow, Context, step, StartEvent, StopEvent
from llama_index.utils.workflow import draw_all_possible_flows  # type: ignore
from events import (
    QueryEvent, ValidationErrorEvent, RetrievalEvent,
    AnswerGeneratedEvent, WorkflowCompletedEvent, NodeWithScore
)


class RAGWorkflow(Workflow):
    def __init__(self, index, llm, timeout=60):
        super().__init__(timeout=timeout)
        self.index = index
        self.llm = llm
        draw_all_possible_flows(self, filename="workflow_steps_graph.html")
        print("✅ קובץ הצעדים נוצר: workflow_steps_graph.html")

    @step
    async def start_and_validate(self, ctx: Context, ev: StartEvent) -> QueryEvent | ValidationErrorEvent:
        query = ev.get("query", "").strip()
        req_id = str(uuid.uuid4())
        if not query:
            return ValidationErrorEvent(request_id=req_id, error_message="השאילתה ריקה.")
        return QueryEvent(request_id=req_id, query=query)

    @step
    async def retrieval_step(self, ctx: Context, ev: QueryEvent) -> RetrievalEvent:
        query_engine = self.index.as_query_engine(similarity_top_k=3)
        res = query_engine.query(ev.query)
        parsed_nodes = [
            NodeWithScore(node_id=n.node.node_id, score=n.score or 0.0, content=n.node.get_content())
            for n in res.source_nodes
        ]
        return RetrievalEvent(request_id=ev.request_id, query=ev.query, nodes=parsed_nodes)

    @step
    async def generation_step(self, ctx: Context, ev: RetrievalEvent) -> AnswerGeneratedEvent:
        context_text = "\n".join([n.content for n in ev.nodes])
        prompt = f"Context:\n{context_text}\n\nQuestion: {ev.query}\nAnswer:"
        response = await self.llm.acomplete(prompt)
        return AnswerGeneratedEvent(request_id=ev.request_id, answer=response.text, context_nodes=ev.nodes)

    @step
    async def end_step(self, ctx: Context, ev: AnswerGeneratedEvent | ValidationErrorEvent) -> WorkflowCompletedEvent:
        answer = ev.error_message if isinstance(ev, ValidationErrorEvent) else ev.answer
        return WorkflowCompletedEvent(answer=answer)
