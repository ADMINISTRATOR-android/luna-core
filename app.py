import os
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def system_status():
    # Looks for Luna UI frontend files
    for path in ['index.html', 'templates/index.html', 'static/index.html']:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    return jsonify({"status": "ONLINE", "system": "LUNA CORE", "version": "v6.5"}), 200

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
        text = data.get('text', '') or data.get('message', '')
        
        headers = {
            "X-API-Key": os.environ.get('CARTESIA_API_KEY'),
            "Cartesia-Version": "2024-06-10",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model_id": "sonic-3.5",
            "transcript": text,
            "voice": {"mode": "id", "id": "248be419-c216-434c-960d-29f00a13b97a"},
            "language": "en",
            "output_format": {
                "container": "mp3",
                "bit_rate": 128000,
                "sample_rate": 44100
            }
        }

        response = requests.post("https://api.cartesia.ai/tts/bytes", headers=headers, json=payload)
        
        if response.status_code != 200:
            return jsonify({"error": f"Cartesia failed: {response.text}"}), response.status_code

        return Response(response.content, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
