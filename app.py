import os
import gradio as gr
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from llama_index.core import VectorStoreIndex, StorageContext, get_response_synthesizer, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.pinecone import PineconeVectorStore

load_dotenv()

# Load existing index from Pinecone (no re-indexing)
# pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
# if "rag-md-index" not in pc.list_indexes().names():
#     pc.create_index(
#         name="rag-md-index",
#         dimension=1536, 
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1")
#     )
# pinecone_index = pc.Index("rag-md-index")

embed_model = CohereEmbedding(
    model_name="embed-english-v3.0",
    cohere_api_key=os.getenv("COHERE_API_KEY")
)

llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")

PERSIST_DIR = "./storage"

if os.path.exists(PERSIST_DIR):
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context, embed_model=embed_model)
else:
    raise Exception("לא נמצאה תיקיית storage. וודאי שהרצת קודם את שלב יצירת האינדקס.")

#vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
# storage_context = StorageContext.from_defaults(vector_store=vector_store)
# index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)

# 1. Retriever
retriever = VectorIndexRetriever(index=index, similarity_top_k=5)

# 2. Postprocessor
postprocessor = SimilarityPostprocessor(similarity_cutoff=0.1)

# 3. Synthesizer
synthesizer = get_response_synthesizer(llm=llm, response_mode="compact")

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    node_postprocessors=[postprocessor],
    response_synthesizer=synthesizer,
)


def chat(message, history):
    response = query_engine.query(message)

    sources = set(
        node.metadata.get("tool", "unknown")
        for node in response.source_nodes
    )
    source_str = f"\n\n📚 *Sources: {', '.join(sources)}*" if sources else ""

    return str(response) + source_str


demo = gr.ChatInterface(
    fn=chat,
    title="🔍 RAG Chat — Cursor & Claude Docs",
    description="Ask anything about Cursor or Claude based on the indexed documentation.")

if __name__ == "__main__":
    demo.launch()
