import os
import uuid
from pathlib import Path
from typing import List
from llama_index.core.workflow import Workflow, Context, step, StartEvent, StopEvent
from llama_index.core.llms import ChatMessage
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core import SimpleDirectoryReader
from llama_index.utils.workflow import draw_all_possible_flows
from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore

from events import (
    IngestEvent, QueryEvent, ValidationErrorEvent, RetrievalEvent,
    AnswerGeneratedEvent, WorkflowCompletedEvent, NodeWithScore, EmbeddingEvent
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PINECONE_INDEX_NAME = "rag-documents"

class RAGWorkflow(Workflow):
    def __init__(self, embed_model, llm, timeout=120):
        super().__init__(timeout=timeout)
        self.embed_model = embed_model
        self.llm = llm
        self.index = None

        try:
            draw_all_possible_flows(self, filename="workflow_steps_graph.html")
            print("✅ Workflow graph generated: workflow_steps_graph.html")
        except Exception as e:
            print(f"⚠️ Could not generate graph: {e}")

    def _get_pinecone_store(self):
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        existing = [i.name for i in pc.list_indexes()]
        if PINECONE_INDEX_NAME not in existing:
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        pinecone_index = pc.Index(PINECONE_INDEX_NAME)
        return PineconeVectorStore(pinecone_index=pinecone_index)

    @step
    async def ingest_step(self, ctx: Context, ev: StartEvent) -> IngestEvent:
        query = ev.get("query", "").strip()

        vector_store = self._get_pinecone_store()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Check if index already has vectors
        stats = vector_store.client.describe_index_stats()
        if stats.get("total_vector_count", 0) > 0:
            self.index = VectorStoreIndex.from_vector_store(vector_store, embed_model=self.embed_model)
            print("✅ Loaded index from Pinecone")
        else:
            cursor_docs = SimpleDirectoryReader(input_dir=str(DATA_DIR / "cursor"), required_exts=[".md"]).load_data()
            claude_docs = SimpleDirectoryReader(input_dir=str(DATA_DIR / "claude"), required_exts=[".md"]).load_data()

            for d in cursor_docs:
                d.metadata["tool"] = "cursor"
            for d in claude_docs:
                d.metadata["tool"] = "claude"

            nodes = MarkdownNodeParser().get_nodes_from_documents(cursor_docs + claude_docs)
            self.index = VectorStoreIndex(nodes, storage_context=storage_context, embed_model=self.embed_model)
            print(f"✅ Indexed {len(nodes)} nodes and saved to Pinecone")

        return IngestEvent(query=query)

    @step
    async def start_and_validate(self, ctx: Context, ev: IngestEvent) -> QueryEvent | ValidationErrorEvent:
        query = ev.query
        req_id = str(uuid.uuid4())
        if not query:
            return ValidationErrorEvent(request_id=req_id, error_message="Query is empty.")
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