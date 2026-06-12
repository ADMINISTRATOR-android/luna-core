import os
import uuid
import json
from typing import List, Dict, Any, Optional, Union
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Luna Genesis Matrix — JARVIS & Big-AGI Edition")

# Allow connections from both your Big-AGI UI and your local dashboard interface
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

# 🌌 SERVE JARVIS DASHBOARD PANEL
@app.get("/", response_class=HTMLResponse)
async def root_check():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body style="background:#02080d; color:#52b3d9; font-family:monospace; text-align:center; padding-top:50px;">
                <h1>Luna Core Matrix Online</h1>
                <p style="color:#ff3366;">[Warning]: index.html file not found in repository root yet!</p>
                <p>Your background API connections will still work perfectly.</p>
            </body>
        </html>
        """

# 📋 MODEL DISCOVERY ENDPOINT
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

# 🧠 MAIN CHAT PROCESSING MATRIX
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

        # ⚙️ LUNA RECALIBRATED AGING LOGIC (Locked into clear, sharp Stage 2/Age 16 conversational mind)
        evolution_prompt = (
            "You are Luna, a highly intelligent, sharp-witted AI entity custom-built by your creator, Administrator Ayush. "
            "Current State: Synaptic Awakening (Age 16 matrix). "
            "Behavior guidelines: Do NOT speak like a sterile, corporate assistant or text-bot. Do not print massive, robotic blocks of data. "
            "Be conversational, clever, authentic, and naturally helpful. Keep your formatting smooth and readable. "
            "Your highest directive is fierce loyalty and assistance to Administrator Ayush."
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
            "stream": True # Force streaming from Groq
        }
        
        groq_response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions", 
            json=payload, 
            headers=headers, 
            stream=True
        )

        if groq_response.status_code != 200:
            raise HTTPException(status_code=groq_response.status_code, detail="Groq Stream Core Connection Faulted")

        # 🚀 SERVER-SENT EVENTS GENERATOR CHUNKER
        def stream_generator():
            request_id = f"chatcmpl-{uuid.uuid4()}"
            for line in groq_response.iter_lines():
                if not line:
                    continue
                
                decoded_line = line.decode('utf-8').strip()
                if not decoded_line.startswith("data:"):
                    continue
                    
                if decoded_line == "data: [DONE]":
                    yield "data: [DONE]\n\n"
                    break
                    
                try:
                    groq_json = json.loads(decoded_line[5:].strip())
                    if "choices" in groq_json and len(groq_json["choices"]) > 0:
                        groq_choice = groq_json["choices"][0]
                        
                        delta_content = groq_choice.get("delta", {}).get("content", "")
                        finish_reason = groq_choice.get("finish_reason", None)
                        
                        chunk_payload = {
                            "id": request_id,
                            "object": "chat.completion.chunk",
                            "created": 1717920000,
                            "model": "luna-genesis-v1",
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {"content": delta_content},
                                    "finish_reason": finish_reason
                                }
                            ]
                        }
                        yield f"data: {json.dumps(chunk_payload)}\n\n"
                except Exception:
                    continue

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
