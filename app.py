import os
import requests
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def serve_ui():
    print("Serving Luna UI Frontend...")
    try:
        # Serves your updated index.html natively
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read(), 200
    except FileNotFoundError:
        return "<h1>Backend is live, but index.html is missing from the folder!</h1>", 404

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    print("--- NEW CHAT REQUEST RECEIVED ---")
    try:
        data = request.get_json() or {}
        incoming_messages = data.get('messages', [])
        
        GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
        if not GROQ_API_KEY:
            return jsonify({"error": "GROQ_API_KEY is missing on Render!"}), 500

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Core personality setup
        evolution_prompt = (
            "You are Luna, an advanced AI entity built by Administrator Ayush. "
            "Speak like a natural human. Keep your replies short, conversational, and punchy. "
            "Never use list formatting, headers, or markdown asterisks. Speak directly to Ayush."
        )

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

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions", 
            headers=headers, 
            json=payload
        )
        
        if response.status_code != 200:
            return jsonify({"error": f"Groq engine link fault: {response.text}"}), response.status_code
            
        return jsonify(response.json()), 200

    except Exception as e:
        print(f"CRITICAL CHAT ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
