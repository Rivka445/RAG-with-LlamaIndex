import os
import uuid
from typing import List, Any
from llama_index.core.workflow import Workflow, Context, step, StartEvent, StopEvent
from llama_index.core.llms import ChatMessage
from llama_index.utils.workflow import draw_all_possible_flows

from events import (
    QueryEvent, ValidationErrorEvent, RetrievalEvent,
    AnswerGeneratedEvent, WorkflowCompletedEvent, NodeWithScore, EmbeddingEvent
)

class RAGWorkflow(Workflow):
    def __init__(self, index, llm, timeout=60):
        super().__init__(timeout=timeout)
        self.index = index
        self.llm = llm
        
        try:
            draw_all_possible_flows(self, filename="workflow_steps_graph.html")
            print("✅ Workflow graph generated: workflow_steps_graph.html")
        except Exception as e:
            print(f"⚠️ Could not generate graph: {e}")

    @step
    async def start_and_validate(self, ctx: Context, ev: StartEvent) -> QueryEvent | ValidationErrorEvent:
        query = ev.get("query", "").strip()
        req_id = str(uuid.uuid4())
        if not query:
            return ValidationErrorEvent(request_id=req_id, error_message="Query is empty.")
        return QueryEvent(request_id=req_id, query=query)

    @step
    async def embedding_step(self, ctx: Context, ev: QueryEvent) -> EmbeddingEvent:
        embed_model = self.index._embed_model 
        query_embedding = embed_model.get_query_embedding(ev.query)
        
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
        context_str = ""
        for i, node in enumerate(ev.nodes, 1):
            context_str += f"--- SOURCE {i} ---\n{node.content}\n\n"

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