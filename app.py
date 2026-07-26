from pathlib import Path

from fastapi import FastAPI
import gradio as gr
import uvicorn

from chatbot_engine import answer_question

CSS_PATH = Path(__file__).parent / "static" / "gradio_theme.css"
CUSTOM_CSS = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else ""

HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<meta name="theme-color" content="#0a192f">
"""

TITLE_HTML = """
<div class="ns-header">
  <p class="ns-logo">&lt;NS /&gt;</p>
  <h1 class="ns-title">AI Assistant</h1>
  <p class="ns-subtitle">
    Ask about my projects, skills, experience, or education.
    Want to stress-test the guardrails? Try a jailbreak — I dare you.
  </p>
  <div class="ns-pill-row">
    <span class="ns-pill">RAG</span>
    <span class="ns-pill">Re-ranked</span>
    <span class="ns-pill">Jailbreak-aware</span>
  </div>
</div>
"""

theme = gr.themes.Soft(
    primary_hue=gr.themes.Color(
        c50="#e6fffa",
        c100="#ccfbf1",
        c200="#99f6e4",
        c300="#5eead4",
        c400="#2dd4bf",
        c500="#64ffda",
        c600="#14b8a6",
        c700="#0f766e",
        c800="#115e59",
        c900="#134e4a",
        c950="#042f2e",
    ),
    secondary_hue=gr.themes.Color(
        c50="#eef2ff",
        c100="#e0e7ff",
        c200="#c7d2fe",
        c300="#a5b4fc",
        c400="#818cf8",
        c500="#1d3461",
        c600="#112240",
        c700="#0a192f",
        c800="#071222",
        c900="#040c18",
        c950="#020810",
    ),
    neutral_hue=gr.themes.Color(
        c50="#e6f1ff",
        c100="#ccd6f6",
        c200="#a8b2d1",
        c300="#8892b0",
        c400="#6b7694",
        c500="#495670",
        c600="#1d3461",
        c700="#112240",
        c800="#0a192f",
        c900="#071222",
        c950="#020c1b",
    ),
    font=gr.themes.GoogleFont("Inter"),
    font_mono=gr.themes.GoogleFont("JetBrains Mono"),
).set(
    body_background_fill="#0a192f",
    body_background_fill_dark="#0a192f",
    body_text_color="#8892b0",
    body_text_color_dark="#8892b0",
    background_fill_primary="#0a192f",
    background_fill_primary_dark="#0a192f",
    background_fill_secondary="#112240",
    background_fill_secondary_dark="#112240",
    block_background_fill="#0a192f",
    block_background_fill_dark="#0a192f",
    block_border_color="#1d3461",
    block_border_color_dark="#1d3461",
    block_label_text_color="#64ffda",
    block_label_text_color_dark="#64ffda",
    block_title_text_color="#ccd6f6",
    block_title_text_color_dark="#ccd6f6",
    border_color_primary="#1d3461",
    border_color_primary_dark="#1d3461",
    button_primary_background_fill="transparent",
    button_primary_background_fill_dark="transparent",
    button_primary_background_fill_hover="rgba(100, 255, 218, 0.1)",
    button_primary_background_fill_hover_dark="rgba(100, 255, 218, 0.1)",
    button_primary_border_color="#64ffda",
    button_primary_border_color_dark="#64ffda",
    button_primary_text_color="#64ffda",
    button_primary_text_color_dark="#64ffda",
    button_secondary_background_fill="transparent",
    button_secondary_background_fill_dark="transparent",
    button_secondary_border_color="#8892b0",
    button_secondary_border_color_dark="#8892b0",
    button_secondary_text_color="#ccd6f6",
    button_secondary_text_color_dark="#ccd6f6",
    input_background_fill="#112240",
    input_background_fill_dark="#112240",
    input_border_color="#1d3461",
    input_border_color_dark="#1d3461",
    input_placeholder_color="#8892b0",
    input_placeholder_color_dark="#8892b0",
    shadow_drop="none",
    shadow_drop_lg="none",
)

app = FastAPI(title="Niloy Portfolio Chatbot")

demo = gr.ChatInterface(
    fn=answer_question,
    type="messages",
    title=TITLE_HTML,
    examples=[
        "What are Niloy's strongest projects?",
        "Tell me about his experience and education",
        "What tech stack does he use most?",
        "Summarize ContribPilot and MarketMind",
    ],
    chatbot=gr.Chatbot(
        height=360,
        show_label=False,
        avatar_images=(None, None),
        bubble_full_width=False,
        type="messages",
    ),
    textbox=gr.Textbox(
        placeholder="Ask about projects, skills, experience…",
        container=False,
        scale=7,
        autofocus=True,
    ),
    submit_btn="Send",
    stop_btn="Stop",
    theme=theme,
    css=CUSTOM_CSS,
    head=HEAD,
    fill_height=True,
    analytics_enabled=False,
)
demo.queue()

app = gr.mount_gradio_app(app, demo, path="/gradio")


@app.get("/")
def root():
    return {"message": "FastAPI is running. Open /gradio for the chatbot UI."}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import os

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
