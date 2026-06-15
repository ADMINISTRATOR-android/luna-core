import os
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def system_status():
    # Smart routing: Look for your Luna UI html file first to display the interface
    for path in ['index.html', 'templates/index.html', 'static/index.html']:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
                
    # Fallback status if the HTML file isn't found in this directory
    return jsonify({
        "status": "ONLINE",
        "system": "LUNA CORE ENGINE",
        "version": "v6.5",
        "connection": "Nebula stable path active"
    }), 200

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    try:
        data = request.get_json() or {}
        user_messages = data.get('messages', [])

        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            return jsonify({"error": "Backend configuration missing GROQ_API_KEY"}), 500

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": user_messages,
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"[GROQ ERROR]: {response.text}")
            return jsonify({"error": f"Groq upstream responded with status {response.status_code}"}), response.status_code

        return jsonify(response.json())

    except Exception as e:
        print(f"[SYSTEM FAULT]: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tts/synthesize', methods=['POST'])
def tts_synthesize():
    try:
        data = request.get_json() or {}
        text_to_speak = data.get('text', '') or data.get('message', '')
        
        if not text_to_speak:
            return jsonify({"error": "No processing text parameter supplied"}), 400

        cartesia_api_key = os.environ.get("CARTESIA_API_KEY")
        if not cartesia_api_key:
            return jsonify({"error": "Backend configuration missing CARTESIA_API_KEY"}), 500

        url = "https://api.cartesia.ai/tts/bytes"
        headers = {
            "X-API-Key": cartesia_api_key,
            "Cartesia-Version": "2024-06-10",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model_id": "sonic-english",
            "transcript": text_to_speak,
            "voice": {
                "mode": "id",
                "id": "248be419-c216-434c-960d-29f00a13b97a"
            },
            "output_format": {
                "container": "mp3",
                "sample_rate": 44100
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"[CARTESIA ERROR]: {response.text}")
            return jsonify({"error": f"Cartesia upstream error status: {response.status_code}"}), response.status_code

        return Response(response.content, mimetype="audio/mpeg")

    except Exception as e:
        print(f"[SYSTEM FAULT]: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
    
