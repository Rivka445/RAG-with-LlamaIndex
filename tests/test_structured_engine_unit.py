import pytest


def test_filter_items_basic():
    from rag.retrieval.structured_engine import StructuredQueryEngine

    # Construct without validation (pydantic) to set attributes directly for unit testing
    try:
        engine = StructuredQueryEngine.model_construct()
    except AttributeError:
        # Fallback for older pydantic versions
        engine = StructuredQueryEngine.construct()

    engine.llm = None
    engine.structured_data = {
        "items": {
            "decisions": [
                {"id": "d1", "title": "Keep secrets", "source": {"tool": "claude"}}
            ],
            "rules": [],
            "warnings": [],
        }
    }

    # Query plan: list all decisions
    plan = {"category": "decisions", "tool_filter": None, "operation": "list", "search_term": None}
    results, text = engine._filter_items(plan)

    assert isinstance(results, list)
    assert len(results) == 1
    assert "Keep secrets" in text

    # Query plan: count
    plan2 = {"category": "decisions", "operation": "count"}
    results2, text2 = engine._filter_items(plan2)
    assert text2.startswith("נמצאו")
