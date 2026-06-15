import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask as FlaskApp, request as flask_request, send_file
from piper.voice import PiperVoice
import requests
from pydantic import BaseModel

# Initialize apps
app = FastAPI()
flask_app = FlaskApp(__name__)

# Paths
MODEL_PATH = "model/en_US-amy-medium.onnx"
CONFIG_PATH = "model/en_US-amy-medium.onnx.json"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Flask TTS Engine
@flask_app.route('/synthesize', methods=['POST'])
def synthesize():
    data = flask_request.get_json()
    text = data.get("text", "")
    if not text: return "No text", 400
    
    voice = PiperVoice.load(MODEL_PATH, config_path=CONFIG_PATH)
    output_file = "output.wav"
    with open(output_file, "wb") as f:
        voice.synthesize(text, f)
    return send_file(output_file, mimetype="audio/wav")

# FastAPI Chat Engine
class ChatRequest(BaseModel):
    messages: list

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    api_messages = [{"role": "system", "content": "You are Luna. Keep replies short and human."}] + req.messages
    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={"model": "llama-3.3-70b-versatile", "messages": api_messages},
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"}
    )
    return JSONResponse(content={"luna_text": res.json()["choices"][0]["message"]["content"]})

# Mount Flask inside FastAPI
app.mount("/tts", WSGIMiddleware(flask_app))
