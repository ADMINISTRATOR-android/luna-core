import os
import requests
import traceback
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def system_status():
    print("PING: System status checked.")
    return jsonify({"status": "ONLINE", "system": "LUNA UI CORE", "engine": "AURA-2"}), 200

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    print("--- NEW CHAT REQUEST RECEIVED ---")
    try:
        data = request.get_json() or {}
        messages = data.get('messages', [])
        print(f"Chat payload received: {len(messages)} messages.")
        
        headers = {
            "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": messages,
            "temperature": 0.7
        }

        print("Sending to Groq...")
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        print(f"Groq Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Groq Error Data: {response.text}")
            
        return jsonify(response.json()), response.status_code
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
        print(f"Text to synthesize: '{text[:30]}...'")
        
        headers = {
            "Authorization": f"Token {os.environ.get('DEEPGRAM_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
        payload = {"text": text}

        print("Sending to Deepgram Aura-2...")
        response = requests.post(url, headers=headers, json=payload)
        print(f"Deepgram Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Deepgram Error Data: {response.text}")
            return jsonify({"error": f"Deepgram failed: {response.text}"}), response.status_code

        print("Deepgram Success! Returning audio stream.")
        return Response(response.content, mimetype="audio/wav")

    except Exception as e:
        print(f"CRITICAL TTS ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
