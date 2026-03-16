from IPython.display import display, HTML
import random
import os
from pathlib import Path
import json
from typing import Any, Dict

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # load .env from project root

from pathlib import Path

from workflows import (
    Workflow,
    Context,
    step,
)
from workflows.events import (
    StartEvent,
    StopEvent,
    Event,
)

from llama_index.core.prompts import RichPromptTemplate

# from llama_index.core.workflow import (
#     StartEvent,
#     StopEvent,
#     Workflow,
#     step,
#     Context,
#     Event
# )
from workflows.events import InputRequiredEvent, HumanResponseEvent

from llama_index.utils.workflow import draw_all_possible_flows
from image_generator import create_poster

from llama_index.llms.openai import OpenAI

llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4.1-mini")

import asyncio
from workflows.server import WorkflowServer

class RetrievalEvent(Event):
    """Holds only the top-K selected Nodes after reranking."""
    top_nodes: List[NodeWithScore]

class ValidationErrorEvent(Event):
    """Emitted if validation fails or no relevant results are found."""
    error_message: str


class EmbeddingsCreatedEvent(Event):
    """Carries the embeddings created for the query."""
    embeddings: List[float]
    query: str


class AnswerGeneratedEvent(Event):
    """Carries the final answer produced by the LLM and its context nodes."""
    answer: str
    context_nodes: List[NodeWithScore]


class InspireWorkflowAdvanced(Workflow):

    @step
    def validate_input_step(state: dict):
        query = state.get("query", "")
        if not query.strip():
            return ValidationErrorEvent(error_message="Query is empty")
        return state  # ממשיכים אם תקין
    
    @step
    def create_embeddings_step(state: dict):
        query = state["query"]
        # placeholder simple embedding: char ords average
        embeddings = [float(ord(c)) for c in query]
        return EmbeddingsCreatedEvent(embeddings=embeddings, query=query)

    @step
    def semantic_search_step(state: dict, embeddings) -> RetrievalEvent:
        # דוגמה לחיפוש סמנטי
        nodes = [NodeWithScore(node_id=str(i), score=1.0/(i+1), content=f"Doc {i}")
                for i in range(10)]
        if not nodes:
            return ValidationErrorEvent(error_message="No search results")
        return RetrievalEvent(nodes=nodes)
         
    @step
    def rerank_step(retrieval_event: RetrievalEvent) -> RerankEvent:
        top_nodes = sorted(retrieval_event.nodes, key=lambda n: n.score, reverse=True)[:3]
        return RerankEvent(top_nodes=top_nodes)
    
    @step
    def llm_processing_step(rerank_event: RerankEvent, query: str) -> AnswerGeneratedEvent:
        answer = f"Answer based on {len(rerank_event.top_nodes)} top nodes for '{query}'"
        return AnswerGeneratedEvent(answer=answer, context_nodes=rerank_event.top_nodes)

inspire_wf = InspireWorkflowAdvanced(timeout=180)
draw_all_possible_flows(
    inspire_wf,
    filename=str(
        Path("7-llamaindex-workflow/inspire/workflows/inspire_wf.html").resolve()
    ),
)


async def main():
    server = WorkflowServer()
    server.add_workflow(
        "inspire_workflow",
        inspire_wf,
        additional_events=[
            RetrievalEvent
        ],
    )
    await server.serve("0.0.0.0", 5050)


if __name__ == "__main__":
    asyncio.run(main())