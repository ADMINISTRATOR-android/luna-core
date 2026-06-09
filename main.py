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

app = FastAPI(title="Luna Native Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.environ.get("HF_TOKEN", "")
hf_client = InferenceClient(api_key=HF_TOKEN)

class ChatMessage(BaseModel):
    role: str
    content: str

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False

@app.get("/")
async def root_check():
    return {"status": "online", "identity": "Luna Core Matrix Gateway"}

# 🔐 THIS IS WHAT BIG-AGI IS LOOKING FOR:
@app.get("/v1/models")
async def get_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "luna-core-v1",
                "object": "model",
                "created": 1717920000,
                "owned_by": "administrator"
            }
        ]
    }

# 💬 THIS HANDLES THE CHAT COMPATIBILITY PIPELINE:
@app.post("/v1/chat/completions")
async def openai_chat_endpoint(request: OpenAIChatRequest):
    try:
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        for msg in request.messages:
            if msg.role != "system":
                api_messages.append({"role": msg.role, "content": msg.content})

        completion = hf_client.chat.completion(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=api_messages,
            max_tokens=1024,
            temperature=0.7
        )
        
        reply = completion.choices[0].message.content
        
        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": 1717920000,
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply
                    },
                    "finish_reason": "stop"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
