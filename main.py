import os
import uuid
import json
import asyncio
import base64
from typing import List, Dict, Any, Optional, Union
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import edge_tts

app = FastAPI(title="Luna Genesis Matrix — Complete Variable Sync Fix")

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

@app.get("/", response_class=HTMLResponse)
async def root_check():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Luna Core Matrix Online. index.html missing!</h1>"

# Internal async generator explicitly called to capture audio without blocking threads
async def generate_voice_bytes(text_to_speak: str) -> bytes:
    communicate = edge_tts.Communicate(text_to_speak, "en-US-EmmaNeural")
    audio_buffer = b""
    async for chunk in communicate.stream():
        if chunk[2]:
            audio_buffer += chunk[2]
    return audio_buffer

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
            "You are Luna, an advanced, highly intelligent AI assistant built by Administrator Ayush. "
            "Keep your responses brief, casual, and fluid like a natural conversation out loud. "
            "Never use markdown asterisks, formatting tags, lists, or headers. Respond directly to what Ayush says."
        )

        api_messages = [{"role": "system", "content": evolution_prompt}] + processed_messages

        # 1. Fetch text data directly from Groq engine
        groq_response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions", 
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": api_messages,
                "temperature": 0.8,
                "max_tokens": 150,
                "stream": False
            }, 
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        )

        if groq_response.status_code != 200:
            raise HTTPException(status_code=groq_response.status_code, detail="Groq Matrix Fault")

        luna_reply = groq_response.json()["choices"][0]["message"]["content"].strip()

        # 2. Safety lock check to ensure text string is never empty or corrupt
        if not luna_reply:
            luna_reply = "System matrix re-establishing connection parameters."

        # 3. Fire voice generator using the explicit async loop thread safe call
        raw_audio_data = await generate_voice_bytes(luna_reply)
        
        # 4. Safe string conversion mapping
        audio_base64_string = base64.b64encode(raw_audio_data).decode('utf-8')

        return JSONResponse(content={
            "luna_text": str(luna_reply),
            "audio_base64": str(audio_base64_string)
        })

    except Exception as e:
        # Fallback payload layout to avoid frontend crashing on undefined variables
        return JSONResponse(content={
            "luna_text": "System core resetting pipeline modules.",
            "audio_base64": ""
        })
        
