import os
import gradio as gr
from dotenv import load_dotenv

from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.openai import OpenAI
from pipeline.workflow import RAGWorkflow
from retrieval.router import build_router

load_dotenv()

embed_model = CohereEmbedding(
    model_name=os.getenv("COHERE_MODEL_NAME", "embed-multilingual-v3.0"),
    cohere_api_key=os.getenv("COHERE_API_KEY"),
)
llm = OpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))

rag_wf = RAGWorkflow(embed_model=embed_model, llm=llm)
router = build_router(rag_wf, llm, embed_model)


async def respond(message, history):
    response = await router.aquery(message)
    history.append(gr.ChatMessage(role="user", content=message))
    history.append(gr.ChatMessage(role="assistant", content=str(response)))
    return "", history


with gr.Blocks(title="RAG System") as demo:
    gr.Markdown("# RAG Assistant")
    chatbot = gr.Chatbot(height=500)
    with gr.Row():
        msg = gr.Textbox(label="שאלה", placeholder="הקלד כאן את שאלתך...", scale=9)
        gr.Button("שלח", variant="primary", scale=1).click(respond, [msg, chatbot], [msg, chatbot])
    msg.submit(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7861)

