from typing import Any, Dict, List, Optional
from llama_index.core.workflow import Event, StartEvent, StopEvent

class IngestEvent(Event):
    query: str

class BaseEvent(Event):
    request_id: str

class QueryEvent(BaseEvent):
    query: str

class ValidationResultEvent(BaseEvent):
    is_valid: bool

class ValidationErrorEvent(BaseEvent):
    error_message: str
    
class EmbeddingEvent(BaseEvent):
    query: str
    embedding: List[float]

class NodeWithScore(Event):
    node_id: str
    score: float
    content: str
    metadata: Dict[str, Any] = {}

class RetrievalEvent(BaseEvent):
    query: str
    nodes: List[NodeWithScore]

class AnswerGeneratedEvent(BaseEvent):
    answer: str
    context_nodes: List[NodeWithScore]

class WorkflowCompletedEvent(StopEvent):
    answer: str