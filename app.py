import os
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def system_status():
    return jsonify({"status": "ONLINE", "system": "LUNA UI CORE", "engine": "AURA-2"}), 200

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    try:
        data = request.get_json() or {}
        messages = data.get('messages', [])
        
        headers = {
            "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": messages,
            "temperature": 0.7
        }

        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tts/synthesize', methods=['POST'])
def tts_synthesize():
    try:
        data = request.get_json() or {}
        text = data.get('text', '')
        
        # Deepgram Aura-2 request configuration
        headers = {
            "Authorization": f"Token {os.environ.get('DEEPGRAM_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        # Using aura-asteria-en model
        url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
        
        payload = {
            "text": text
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return jsonify({"error": f"Deepgram failed: {response.text}"}), response.status_code

        # Return audio stream
        return Response(response.content, mimetype="audio/wav")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
