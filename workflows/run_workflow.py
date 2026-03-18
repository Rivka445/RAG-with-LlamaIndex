import os
from pathlib import Path
import gradio as gr
from dotenv import load_dotenv
import asyncio

from llama_index.core import StorageContext, load_index_from_storage
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.openai import OpenAI
from server import RAGWorkflow

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PERSIST_DIR = str((BASE_DIR.parent / "storage").resolve())

embed_model = CohereEmbedding(model_name="embed-english-v3.0", cohere_api_key=os.getenv("COHERE_API_KEY"))
llm = OpenAI(model="gpt-4o")

storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
index = load_index_from_storage(storage_context, embed_model=embed_model)

rag_wf = RAGWorkflow(index=index, llm=llm)

async def chat_interface(query):
    result = await rag_wf.run(query=query)
    return result.answer

with gr.Blocks(title="LlamaIndex Workflow RAG") as demo:
    gr.Markdown("# 🪜 RAG Workflow עם תצוגת Steps")
    
    with gr.Row():
        with gr.Column():
            query_input = gr.Textbox(label="שאלה")
            submit_btn = gr.Button("שלח", variant="primary")
        
        with gr.Column():
            answer_output = gr.Textbox(label="תשובה")
    
    gr.Markdown("### 📊 תרשים מבנה התהליך")
    html_file = gr.File(value="workflow_steps_graph.html", label="הורד תרשים זרימה HTML")

    submit_btn.click(fn=chat_interface, inputs=query_input, outputs=answer_output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)