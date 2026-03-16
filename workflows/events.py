from llama_index.core.workflows import Event
from llama_index.core.schema import NodeWithScore, Document
from typing import List

class RetrievalEvent(Event):
    """נושא את כל ה-Nodes שחזרו מהחיפוש הסמנטי (למשל 10 המובילים)"""
    nodes: List[NodeWithScore]

class RerankEvent(Event):
    """נושא רק את ה-3 ה-Nodes הכי מתאימים שנבחרו"""
    top_nodes: List[NodeWithScore]

class ValidationErrorEvent(Event):
    """אירוע שמופעל אם לא נמצאו תוצאות רלוונטיות"""
    error_message: str

class EmbeddingsCreatedEvent(Event):
    """נושא את הוקטורים שנוצרו מהשאילתה"""
    embeddings: List[float]
    query: str

class AnswerGeneratedEvent(Event):
    """נושא את התשובה הסופית שהופקה על ידי LLM"""
    answer: str
    context_nodes: List[NodeWithScore]