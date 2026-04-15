import uuid
from typing import List
from llama_index.core.workflow import Workflow, Context, step, StartEvent, StopEvent
from llama_index.core.llms import ChatMessage

from pipeline.events import (
    IngestEvent, QueryEvent, ValidationErrorEvent, RetrievalEvent,
    AnswerGeneratedEvent, WorkflowCompletedEvent, NodeWithScore, EmbeddingEvent
)
from pipeline.indexer import load_or_build_index

class RAGWorkflow(Workflow):
    def __init__(self, embed_model, llm, timeout=120):
        super().__init__(timeout=timeout)
        self.embed_model = embed_model
        self.llm = llm
        self.index = None


    @step
    async def ingest_step(self, ctx: Context, ev: StartEvent) -> IngestEvent:
        query = ev.get("query", "").strip()
        if self.index is None:
            self.index = load_or_build_index(self.embed_model)
        return IngestEvent(query=query)

    @step
    async def start_and_validate(self, ctx: Context, ev: IngestEvent) -> QueryEvent | ValidationErrorEvent:
        query = ev.query
        req_id = str(uuid.uuid4())
        return QueryEvent(request_id=req_id, query=query)

    @step
    async def embedding_step(self, ctx: Context, ev: QueryEvent) -> EmbeddingEvent:
        query_embedding = self.embed_model.get_query_embedding(ev.query)
        
        return EmbeddingEvent(
            request_id=ev.request_id, 
            query=ev.query, 
            embedding=query_embedding
        )

    @step
    async def retrieval_step(self, ctx: Context, ev: EmbeddingEvent) -> RetrievalEvent:
        retriever = self.index.as_retriever(similarity_top_k=10)
        nodes_with_score = retriever.retrieve(ev.query)
        
        parsed_nodes = [
            NodeWithScore(
                node_id=n.node.node_id, 
                score=n.score or 0.0, 
                content=n.node.get_content()
            )
            for n in nodes_with_score
        ]
        return RetrievalEvent(request_id=ev.request_id, query=ev.query, nodes=parsed_nodes)

    @step
    async def generation_step(self, ctx: Context, ev: RetrievalEvent) -> AnswerGeneratedEvent:
        context_str = "\n".join(f"--- SOURCE {i} ---\n{node.content}" for i, node in enumerate(ev.nodes, 1))

        system_prompt = (
            "You are a professional Research Assistant. Your goal is to answer the user's question "
            "strictly using the provided context. Follow these rules:\n"
            "1. If the answer is not contained within the context, state that you do not know.\n"
            "2. Do not use outside knowledge or make up facts.\n"
            "3. Cite your sources using the format [Source X] at the end of relevant sentences.\n"
            "4. Keep the tone objective and concise."
        )

        user_prompt = (
            f"Technical Context:\n{context_str}\n"
            f"User Inquiry: {ev.query}\n"
            "Look specifically for URLs, ports, hostnames, and configuration settings. "
            "If the information is technical, provide the exact values found."
        )

        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt),
        ]
        
        response = await self.llm.achat(messages)
        
        return AnswerGeneratedEvent(
            request_id=ev.request_id, 
            answer=str(response.message.content), 
            context_nodes=ev.nodes
        )

    @step
    async def end_step(self, ctx: Context, ev: AnswerGeneratedEvent | ValidationErrorEvent) -> WorkflowCompletedEvent:
        answer = ev.error_message if isinstance(ev, ValidationErrorEvent) else ev.answer
        return WorkflowCompletedEvent(answer=answer)