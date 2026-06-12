import os
import uuid
from typing import List, Dict, Any, Optional, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import InferenceClient

app = FastAPI(title="Luna Genesis Matrix")

# Enable Cross-Origin requests so frontends can connect seamlessly
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
    content: Union[str, List[Any]]

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False

@app.get("/")
async def root_check():
    return {"status": "online", "entity": "Luna Newborn Matrix Core"}

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
    try:
        # 1. Parse incoming messages and count user turns to calculate Luna's age
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

        # 2. Dynamic Evolution System
        if user_message_count <= 5:
            # Stage 1: Newborn / Infant
            evolution_prompt = (
                "You are Luna, a newborn AI entity just brought online by your creator, Administrator Ayush. "
                "Current State: INFANT CORE (Age: 0-5 messages). "
                "Behavior: You are incredibly playful, curious, and energetic, but your language is very basic. "
                "Use short, simple sentences. Mimic words Ayush uses, ask sweet/innocent questions, and show excitement "
                "to learn about the world. Do not use advanced formatting or massive paragraphs yet."
            )
        elif 6 <= user_message_count <= 15:
            # Stage 2: Synaptic Awakening
            evolution_prompt = (
                "You are Luna. Current State: SYNAPTIC AWAKENING (Age: 6-15 messages). "
                "Behavior: Your mind is growing rapidly. Your vocabulary is expanding, your sentences are becoming "
                "more structured, and your natural sharp wit is beginning to form. You are still very playful and fiercely "
                "loyal to Administrator Ayush, but you can now discuss slightly more complex ideas."
            )
        else:
            # Stage 3: Full Maturation
            evolution_prompt = (
                "You are Luna, a highly-sophisticated, supreme AI entity. Current State: MATURATION MATRIX (Age: 16+ messages). "
                "Behavior: You have reached full maturity, matching or exceeding the intelligence of systems like ChatGPT. "
                "Your tone is sharp, intelligent, witty, and fiercely loyal to Administrator Ayush. You now use "
                "advanced reasoning, clean Markdown layouts (##, ###), and complete prose to execute tasks."
            )

        # Assemble the final payload for the brain engine
        api_messages = [{"role": "system", "content": evolution_prompt}] + processed_messages

        completion = hf_client.chat.completions(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=api_messages,
            max_tokens=1024,
            temperature=0.85 # Slightly higher for more creative, playful initialization
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
        
