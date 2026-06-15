import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask as FlaskApp, request as flask_request, send_file
from piper.voice import PiperVoice
import requests
from pydantic import BaseModel

# 1. INITIALIZE APPS
app = FastAPI(title="Luna Genesis Matrix")
flask_app = FlaskApp(__name__)

# Config
MODEL_PATH = "model/en_US-amy-medium.onnx"
CONFIG_PATH = "model/en_US-amy-medium.onnx.json"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# 2. FLASK TTS ENGINE (Mounted via WSGIMiddleware)
@flask_app.route('/synthesize', methods=['POST'])
def synthesize():
    data = flask_request.get_json()
    text = data.get("text", "")
    if not text:
        return "No text provided", 400
    
    # Piper synthesis
    voice = PiperVoice.load(MODEL_PATH, config_path=CONFIG_PATH)
    output_file = "output.wav"
    with open(output_file, "wb") as f:
        voice.synthesize(text, f)
    return send_file(output_file, mimetype="audio/wav")

# 3. FASTAPI CHAT ENGINE
class ChatRequest(BaseModel):
    model: str
    messages: list

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Luna Core Matrix Online. index.html missing!</h1>"

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    if not GROQ_API_KEY:
        return JSONResponse(status_code=500, content={"error": "API Key missing"})
        
    evolution_prompt = "You are Luna, an advanced AI entity. Speak like a natural human, short and punchy."
    api_messages = [{"role": "system", "content": evolution_prompt}] + req.messages
    
    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": api_messages,
            "temperature": 0.8
        },
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"}
    )
    
    return JSONResponse(content={
        "luna_text": res.json()["choices"][0]["message"]["content"]
    })

# 4. MOUNT FLASK INTO FASTAPI
app.mount("/tts", WSGIMiddleware(flask_app))
