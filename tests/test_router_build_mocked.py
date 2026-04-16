import json
from types import SimpleNamespace


def test_build_router_reads_structured_json_and_constructs_tools(monkeypatch, tmp_path):
    import rag.retrieval.router as router_mod

    # Create a fake structured JSON file
    structured = {"items": {}}
    sfile = tmp_path / "structured.json"
    sfile.write_text(json.dumps(structured), encoding="utf-8")

    # Point the structured path to our temp file
    import rag.retrieval.structured_engine as se
    monkeypatch.setattr(se, "STRUCTURED_JSON_PATH", sfile)

    # Replace QueryEngineTool.from_defaults and RouterQueryEngine to capture usage
    captured = {}

    class FakeQueryEngineTool:
        @staticmethod
        def from_defaults(query_engine=None, name=None, description=None):
            captured.setdefault('tools', []).append(name)
            return f"TOOL:{name}"

    class FakeRouter:
        def __init__(self, selector=None, query_engine_tools=None, verbose=False):
            self.selector = selector
            self.tools = query_engine_tools

    monkeypatch.setattr(router_mod, "QueryEngineTool", FakeQueryEngineTool)
    monkeypatch.setattr(router_mod, "RouterQueryEngine", FakeRouter)
    monkeypatch.setattr(router_mod, "LLMSingleSelector", SimpleNamespace(from_defaults=lambda llm=None: "SELECTOR"))

    # Avoid pydantic validation by replacing StructuredQueryEngine constructor
    monkeypatch.setattr(router_mod, "StructuredQueryEngine", lambda llm=None, structured_data=None: "STRUCT_ENGINE")

    # Dummy workflow/llm/embed
    rag_wf = SimpleNamespace()
    llm = object()
    embed = object()

    router = router_mod.build_router(rag_wf, llm, embed)

    assert isinstance(router, FakeRouter)
    assert hasattr(router, 'tools')
    assert 'semantic_search' in captured.get('tools', [])
