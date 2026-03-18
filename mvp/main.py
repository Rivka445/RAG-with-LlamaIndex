import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore

load_dotenv()

# 1. Loading
cursor_docs = SimpleDirectoryReader(input_dir="./data/cursor", required_exts=[".md"]).load_data()
claude_docs = SimpleDirectoryReader(input_dir="./data/claude", required_exts=[".md"]).load_data()

for d in cursor_docs:
    d.metadata["tool"] = "cursor"
for d in claude_docs:
    d.metadata["tool"] = "claude"

documents = cursor_docs + claude_docs

# 2. Chunking
parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents)

# 3. Embedding
embed_model = CohereEmbedding(
    model_name="embed-english-v3.0",
    cohere_api_key=os.getenv("COHERE_API_KEY")
)

# 4. Pinecone

PERSIST_DIR = "./storage" 

# pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# index_name = "rag-md-index"
# if index_name not in [i.name for i in pc.list_indexes()]:
#     pc.create_index(
#         name=index_name,
#         dimension=1024,
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1")
#     )

# pinecone_index = pc.Index(index_name)

# 5. VectorStoreIndex with Pinecone

if not os.path.exists(PERSIST_DIR):
    index = VectorStoreIndex(
        nodes,
        embed_model=embed_model
    )
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context, embed_model=embed_model)

query_engine = index.as_query_engine()

# vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
# storage_context = StorageContext.from_defaults(vector_store=vector_store)

# index = VectorStoreIndex(
#     nodes,
#     storage_context=storage_context,
#     embed_model=embed_model
# )



