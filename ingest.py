import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.cohere import CohereEmbedding

load_dotenv()

# 1. טעינת המסמכים
print("Loading documents...")
cursor_docs = SimpleDirectoryReader(input_dir="./data/cursor", required_exts=[".md"]).load_data()
claude_docs = SimpleDirectoryReader(input_dir="./data/claude", required_exts=[".md"]).load_data()

for d in cursor_docs: d.metadata["tool"] = "cursor"
for d in claude_docs: d.metadata["tool"] = "claude"
documents = cursor_docs + claude_docs

# 2. פירוק לצ'אנקים
print("Parsing nodes...")
parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents)

# 3. הגדרת מודל ה-Embedding
embed_model = CohereEmbedding(
    model_name="embed-english-v3.0",
    cohere_api_key=os.getenv("COHERE_API_KEY")
)

# 4. יצירת האינדקס ושמירה למחשב
print("Creating index and saving to ./storage...")
index = VectorStoreIndex(nodes, embed_model=embed_model)

# יצירת התיקייה ושמירת הקבצים
index.storage_context.persist(persist_dir="./storage")
print("Done! You can now run app.py")