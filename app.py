import os
import requests
import traceback
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS globally so your separate static frontend can talk to it safely
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def system_status():
    print("PING: System status checked.")
    return jsonify({
        "status": "ONLINE", 
        "system": "LUNA UI CORE", 
        "engine": "AURA-2"
    }), 200

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    print("--- NEW CHAT REQUEST RECEIVED ---")
    try:
        data = request.get_json() or {}
        incoming_messages = data.get('messages', [])
        print(f"Chat payload received: {len(incoming_messages)} messages.")
        
        GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
        if not GROQ_API_KEY:
            return jsonify({"error": "GROQ_API_KEY is missing on Render!"}), 500

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # System evolution behavior blueprint merged from your legacy core setup
        evolution_prompt = (
            "You are Luna, an advanced AI entity built by Administrator Ayush. "
            "Speak like a natural human. Keep your replies short, conversational, and punchy. "
            "Never use list formatting, headers, or markdown asterisks. Speak directly to Ayush."
        )

        # Build clean execution payload wrapping your evolution system rules
        processed_messages = [{"role": "system", "content": evolution_prompt}]
        for msg in incoming_messages:
            processed_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        payload = {
            "model": "llama3-8b-8192",
            "messages": processed_messages,
            "temperature": 0.8
        }

        print("Sending request to Groq Engine...")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions", 
            headers=headers, 
            json=payload
        )
        print(f"Groq Upstream Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Groq Error Log: {response.text}")
            return jsonify({"error": f"Groq engine link fault: {response.text}"}), response.status_code
            
        return jsonify(response.json()), 200

    except Exception as e:
        print(f"CRITICAL CHAT ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/tts/synthesize', methods=['POST'])
def tts_synthesize():
    print("--- NEW TTS REQUEST RECEIVED ---")
    try:
        data = request.get_json() or {}
        text = data.get('text', '')
        print(f"Text payload to synthesize: '{text[:40]}...'")
        
        DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY')
        if not DEEPGRAM_API_KEY:
            return jsonify({"error": "DEEPGRAM_API_KEY is missing on Render!"}), 500

        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }
        
        url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
        payload = {"text": text}

        print("Streaming compilation payload to Deepgram Aura-2...")
        response = requests.post(url, headers=headers, json=payload)
        print(f"Deepgram Upstream Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Deepgram Error Log: {response.text}")
            return jsonify({"error": f"Deepgram pipeline failed: {response.text}"}), response.status_code

        print("Deepgram compilation complete! Streaming audio raw binary channel back...")
        return Response(response.content, mimetype="audio/wav")

    except Exception as e:
        print(f"CRITICAL TTS ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Dynamically bind to the port assigned by Render environmental setups
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
