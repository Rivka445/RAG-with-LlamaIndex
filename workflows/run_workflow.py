import os
from pathlib import Path
import gradio as gr
from dotenv import load_dotenv
import asyncio

from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.openai import OpenAI
from server import RAGWorkflow

load_dotenv()

embed_model = CohereEmbedding(
    model_name="embed-multilingual-v3.0",
    cohere_api_key=os.getenv("COHERE_API_KEY")
)
llm = OpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))

rag_wf = RAGWorkflow(embed_model=embed_model, llm=llm)

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
        chat_history.append(gr.ChatMessage(role="user", content=message))
        chat_history.append(gr.ChatMessage(role="assistant", content=bot_message))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit_btn.click(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860
    )