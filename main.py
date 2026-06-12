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

app = FastAPI(title="Luna Genesis Matrix — Fixed Human Voice Edition")

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

        # Fetch response text from Groq
        groq_response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions", 
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": api_messages,
                "temperature": 0.85,
                "max_tokens": 200,
                "stream": False
            }, 
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        )

        if groq_response.status_code != 200:
            raise HTTPException(status_code=groq_response.status_code, detail="Groq Link Fault")

        luna_reply = groq_response.json()["choices"][0]["message"]["content"]

        # 🎙️ Generate the clean Edge-TTS audio file into memory
        communicate = edge_tts.Communicate(luna_reply, "en-US-EmmaNeural")
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk[2]:
                audio_data += chunk[2]

        # Convert raw audio bytes into a clean, browser-safe text string
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        # Send everything back as a rock-solid JSON package
        return JSONResponse(content={
            "luna_text": luna_reply,
            "audio_base64": audio_base64
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
