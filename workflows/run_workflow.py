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

embed_model = CohereEmbedding(
    model_name="embed-multilingual-v3.0", 
    cohere_api_key=os.getenv("COHERE_API_KEY")
)
llm = OpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))

storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
index = load_index_from_storage(storage_context, embed_model=embed_model)

rag_wf = RAGWorkflow(index=index, llm=llm)

async def chat_logic(message):
    try:
        result = await rag_wf.run(query=message)
        return result.answer
    except Exception as e:
        return f"Error: {str(e)}"

with gr.Blocks(title="RAG System") as demo:
    gr.Markdown("# RAG Assistant")
    
    chatbot = gr.Chatbot(height=500)
    
    with gr.Row():
        msg = gr.Textbox(
            label="שאלה",
            placeholder="הקלד כאן את שאלתך...",
            scale=9
        )
        submit_btn = gr.Button("שלח", variant="primary", scale=1)

    gr.Markdown("### Workflow Visualization")
    gr.File(value="workflow_steps_graph.html", label="Workflow Graph HTML")

    def respond(message, chat_history):
        bot_message = asyncio.run(chat_logic(message))
        chat_history.append((message, bot_message))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit_btn.click(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860
    )