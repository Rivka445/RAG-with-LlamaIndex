import json
from types import SimpleNamespace


def test_load_or_build_index_creates_and_persists(monkeypatch, tmp_path):
    import rag.pipeline.indexer as indexer

    # Prepare fake data and index storage dir
    tmp_index_dir = tmp_path / "index_storage"
    monkeypatch.setattr(indexer, "INDEX_STORAGE_DIR", tmp_index_dir)

    # Fake documents returned by SimpleDirectoryReader
    fake_doc = SimpleNamespace(metadata={}, get_content=lambda: "doc content")

    class FakeReader:
        def __init__(self, input_dir=None, required_exts=None):
            pass

        def load_data(self):
            return [fake_doc]

    monkeypatch.setattr(indexer, "SimpleDirectoryReader", FakeReader)

    # Fake MarkdownNodeParser that turns documents into nodes
    class FakeNodeParser:
        def get_nodes_from_documents(self, docs):
            return [SimpleNamespace(node_id="n1", get_content=lambda: "content")]

    monkeypatch.setattr(indexer, "MarkdownNodeParser", lambda: FakeNodeParser())

    persisted = {}

    class FakeStorageContext:
        @staticmethod
        def from_defaults(persist_dir=None):
            return SimpleNamespace()

    # Fake VectorStoreIndex with storage_context.persist
    class FakeIndex:
        def __init__(self, nodes, embed_model=None):
            self.nodes = nodes
            self.storage_context = SimpleNamespace(persist=lambda persist_dir: persisted.setdefault('persisted', True))

    monkeypatch.setattr(indexer, "VectorStoreIndex", FakeIndex)

    # Call function with a dummy embed_model
    result = indexer.load_or_build_index(embed_model=object())

    assert hasattr(result, "storage_context")
    assert persisted.get('persisted', False) is True
