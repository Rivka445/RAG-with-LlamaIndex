def test_import_rag_and_workflow():
    import rag
    from rag.pipeline.workflow import RAGWorkflow

    # Basic smoke assertions
    assert rag is not None
    assert callable(RAGWorkflow)

def test_structured_json_exists():
    from rag.retrieval.structured_engine import STRUCTURED_JSON_PATH
    assert STRUCTURED_JSON_PATH.exists()
