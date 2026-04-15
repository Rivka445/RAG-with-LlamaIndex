from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core import SimpleDirectoryReader

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INDEX_STORAGE_DIR = Path(__file__).resolve().parent.parent / "index_storage"


def load_or_build_index(embed_model):
    if INDEX_STORAGE_DIR.exists():
        storage_context = StorageContext.from_defaults(persist_dir=str(INDEX_STORAGE_DIR))
        index = load_index_from_storage(storage_context, embed_model=embed_model)
    else:
        cursor_docs = SimpleDirectoryReader(input_dir=str(DATA_DIR / "cursor"), required_exts=[".md"]).load_data()
        claude_docs = SimpleDirectoryReader(input_dir=str(DATA_DIR / "claude"), required_exts=[".md"]).load_data()

        for d in cursor_docs:
            d.metadata["tool"] = "cursor"
        for d in claude_docs:
            d.metadata["tool"] = "claude"

        nodes = MarkdownNodeParser().get_nodes_from_documents(cursor_docs + claude_docs)
        index = VectorStoreIndex(nodes, embed_model=embed_model)
        index.storage_context.persist(persist_dir=str(INDEX_STORAGE_DIR))

    return index
