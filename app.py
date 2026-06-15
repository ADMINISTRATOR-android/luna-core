import os
import requests
import io
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="Luna Core Matrix - Cartesia Sonic Edition")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
CARTESIA_API_KEY = os.environ.get("CARTESIA_API_KEY", "").strip()

# Cartesia Configurations
CARTESIA_MODEL = "sonic-english"
# A crystal-clear, premium cybernetic female voice profile
CARTESIA_VOICE_ID = "694f9389-faee-4321-b3fb-ee0b47f6f695" 

class ChatRequest(BaseModel):
    messages: list

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Critical Error: index.html missing from root directory!</h1>"

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    if not GROQ_API_KEY:
        return JSONResponse(status_code=400, content={"error": "GROQ_API_KEY is missing from Render environment variables."})
    
    try:
        api_messages = [{"role": "system", "content": "You are Luna. Keep replies short and human."}] + req.messages
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json={"model": "llama-3.3-70b-versatile", "messages": api_messages},
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            timeout=10
        )
        res_data = res.json()
        return JSONResponse(content={"luna_text": res_data["choices"][0]["message"]["content"]})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Groq Gateway Error: {str(e)}"})

@app.post("/tts/synthesize")
async def synthesize(data: dict):
    text = data.get("text", "").strip()
    if not text:
        return JSONResponse(status_code=400, content={"error": "No directive coordinates provided for vocalization."})
    if not CARTESIA_API_KEY:
        return JSONResponse(status_code=400, content={"error": "CARTESIA_API_KEY is missing from Render environment variables."})

    try:
        response = requests.post(
            "https://api.cartesia.ai/tts/bytes",
            headers={
                "X-API-Key": CARTESIA_API_KEY,
                "Cartesia-Version": "2024-06-10",
                "Content-Type": "application/json"
            },
            json={
                "model_id": CARTESIA_MODEL,
                "transcript": text,
                "voice": {
                    "mode": "id",
                    "id": CARTESIA_VOICE_ID
                },
                "output_format": {
                    "container": "wav",
                    "encoding": "linear16",
                    "sample_rate": 24000
                }
            },
            timeout=10
        )

        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content={"error": "Cartesia matrix initialization rejected."})

        return StreamingResponse(io.BytesIO(response.content), media_type="audio/wav")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Matrix Streaming Failure: {str(e)}"})
        
