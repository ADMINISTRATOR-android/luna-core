import os
from typing import List, Any, Optional, Union
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Luna Genesis Matrix — Clean Text Core")

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
            "You are Luna, an advanced AI entity built by Administrator Ayush. "
            "Speak like a natural human. Keep your replies short, conversational, and punchy. "
            "Never use list formatting, headers, or markdown asterisks. Speak directly to Ayush."
        )

        api_messages = [{"role": "system", "content": evolution_prompt}] + processed_messages

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
            raise HTTPException(status_code=groq_response.status_code, detail="Groq Link Fault")

        luna_reply = groq_response.json()["choices"][0]["message"]["content"].strip()

        return JSONResponse(content={
            "luna_text": str(luna_reply)
        })

    except Exception as e:
        return JSONResponse(content={
            "luna_text": "Connection re-established. Standing by."
        })
        
