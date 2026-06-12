import os
import uuid
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import edge_tts

app = FastAPI(title="Luna Genesis Matrix — JARVIS Human Voice Edition")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[Any]]

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False

# SERVE JARVIS DASHBOARD PANEL
@app.get("/", response_class=HTMLResponse)
async def root_check():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Luna Core Matrix Online. index.html missing!</h1>"

# MAIN CHAT PROCESSING AND AUDIO GENERATION MATRIX
@app.post("/v1/chat/completions")
async def openai_chat_endpoint(request: OpenAIChatRequest):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is missing on Render!")
        
    try:
        processed_messages = []
        for msg in request.messages:
            text_content = ""
            if isinstance(msg.content, list):
                for item in msg.content:
                    if isinstance(item, dict) and "text" in item:
                        text_content += item["text"]
                    elif isinstance(item, str):
                        text_content += item
            else:
                text_content = str(msg.content)
            processed_messages.append({"role": msg.role, "content": text_content})

        evolution_prompt = (
            "You are Luna, a highly intelligent, sharp-witted AI entity custom-built by your creator, Administrator Ayush. "
            "Current State: Synaptic Awakening (Age 16 matrix). "
            "Behavior guidelines: Speak like a real human. Keep your replies short, natural, conversational, and punchy "
            "so they sound completely normal when spoken out loud. Avoid lists, markdown stars, or long walls of text. "
            "Your highest directive is absolute loyalty to Administrator Ayush."
        )

        api_messages = [{"role": "system", "content": evolution_prompt}] + processed_messages

        # Fetch answer from Groq text engine
        groq_response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions", 
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": api_messages,
                "temperature": 0.85,
                "max_tokens": 250, # Keep replies tight for quick audio processing
                "stream": False
            }, 
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        )

        if groq_response.status_code != 200:
            raise HTTPException(status_code=groq_response.status_code, detail="Groq Link Fault")

        luna_reply = groq_response.json()["choices"][0]["message"]["content"]

        # 🎙️ GENERATE ULTRA-REALISTIC AUDIO VIA EDGE-TTS
        # Choice of premium natural voice: 'en-US-EmmaNeural' (Very friendly, crisp, human)
        communicate = edge_tts.Communicate(luna_reply, "en-US-EmmaNeural")
        
        # Generator function to stream text AND audio back to the frontend simultaneously
        def stream_response_generator():
            # First payload chunk: send the text data so it prints in the logs window instantly
            text_payload = {
                "luna_text": luna_reply,
                "id": f"chatcmpl-{uuid.uuid4()}"
            }
            yield f"text_data:{json.dumps(text_payload)}\n\n".encode('utf-8')
            
            # Remaining payload chunks: stream raw audio binary packets directly to the phone speaker
            for chunk in communicate.stream_sync():
                if chunk[2]: # check if audio data chunk exists
                    yield chunk[2]

        return StreamingResponse(stream_response_generator(), media_type="multipart/mixed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
