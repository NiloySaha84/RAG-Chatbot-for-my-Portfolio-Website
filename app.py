from fastapi import FastAPI
import gradio as gr
import uvicorn

from chatbot_engine import answer_question

app = FastAPI(title="Niloy Portfolio Chatbot")


demo = gr.ChatInterface(
    fn=answer_question,
    title="Niloy Saha Portfolio Chatbot",
    description="Ask questions about Niloy's projects, education, experience, and skills.",
)

app = gr.mount_gradio_app(app, demo, path="/gradio")


@app.get("/")
def root():
    return {"message": "FastAPI is running. Open /gradio for the chatbot UI."}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)