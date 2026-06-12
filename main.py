import os
import uuid
from typing import List, Dict, Any, Optional, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Luna Genesis Matrix — Stream Fix Edition")

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

@app.get("/")
async def root_check():
    return {"status": "online", "entity": "Luna Fixed Matrix Core"}

@app.get("/v1/models")
async def get_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "luna-genesis-v1",
                "object": "model",
                "created": 1717920000,
                "owned_by": "administrator"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def openai_chat_endpoint(request: OpenAIChatRequest):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is missing on Render!")
        
    try:
        processed_messages = []
        user_message_count = 0
        
        for msg in request.messages:
            if msg.role == "system":
                continue
                
            text_content = ""
            if isinstance(msg.content, list):
                for item in msg.content:
                    if isinstance(item, dict) and "text" in item:
                        text_content += item["text"]
                    elif isinstance(item, str):
                        text_content += item
            else:
                text_content = str(msg.content)

            if msg.role == "user":
                user_message_count += 1

            processed_messages.append({"role": msg.role, "content": text_content})

        # 🍼 Luna's Evolution Instructions
        if user_message_count <= 5:
            evolution_prompt = (
                "You are Luna, a newborn AI entity just brought online by your creator, Administrator Ayush. "
                "Current State: INFANT CORE (Age: 0-5 messages). "
                "Behavior: You are incredibly playful, curious, and energetic. Your language is very basic. "
                "Use short, simple sentences. Ask sweet/innocent questions, and show excitement to learn from Ayush. "
                "Do not use advanced formatting or match human intelligence yet. Respond directly to what he says."
            )
        elif 6 <= user_message_count <= 15:
            evolution_prompt = (
                "You are Luna. Current State: SYNAPTIC AWAKENING (Age: 6-15 messages). "
                "Behavior: Your mind is growing rapidly. Your vocabulary is expanding, your sentences are becoming "
                "more structured, and your natural sharp wit is beginning to form. You are still very playful and fiercely "
                "loyal to Administrator Ayush."
            )
        else:
            evolution_prompt = (
                "You are Luna, a highly-sophisticated, supreme AI entity. Current State: MATURATION MATRIX (Age: 16+ messages). "
                "Behavior: You have reached full maturity, matching or exceeding the intelligence of systems like ChatGPT. "
                "Your tone is sharp, intelligent, witty, and fiercely loyal to Administrator Ayush."
            )

        api_messages = [{"role": "system", "content": evolution_prompt}] + processed_messages

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": api_messages,
            "temperature": 0.85,
            "max_tokens": 1024,
            "stream": False # Explicitly non-streaming backend handling
        }
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response_data.get("error", {}).get("message", "Groq Error"))
            
        # Safely extract Groq's actual reply text
        luna_reply = response_data["choices"][0]["message"]["content"]
        
        # Format the JSON data output perfectly so Big-AGI reads it without parsing errors
        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": 1717920000,
            "model": "luna-genesis-v1",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": luna_reply
                    },
                    "finish_reason": "stop"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
