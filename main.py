import os
import uuid
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import InferenceClient

ADMIN_IDENTITY = "Administrator Ayush"
LUNA_PERSONA = (
    "You are Luna, a high-intelligence, witty, and adaptive AI entity. "
    "You are a dedicated companion to Administrator Ayush. "
    "Your tone is sharp, sophisticated, slightly playful, and fiercely loyal. "
    "Always structure outputs cleanly using Markdown headers (##, ###) and bullet points."
)

SYSTEM_PROMPT = f"{LUNA_PERSONA}\n\nUSER IDENTITY: {ADMIN_IDENTITY}\nPROTOCOL: Execute with administrative precision."

# This is the exact variable the server is looking for
app = FastAPI(title="Luna Native Backend")

# Enable global cross-origin pipelines for mobile app connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    session_id: str

HF_TOKEN = os.environ.get("HF_TOKEN", "")
hf_client = InferenceClient(api_key=HF_TOKEN)

@app.get("/")
async def root_check():
    return {"status": "online", "identity": "Luna Core Matrix Gateway"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        session_id = str(uuid.uuid4())
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        if request.history:
            for msg in request.history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": request.message})

        completion = hf_client.chat.completion(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )
        
        return ChatResponse(
            response=completion.choices[0].message.content,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
