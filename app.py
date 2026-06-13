from flask import Flask, request, send_file, send_from_directory
from kokoro import KPipeline
import soundfile as sf
import io
import os

# 1. Point Flask to the 'static' folder where your index.html lives
app = Flask(__name__, static_folder='static')

# Initialize pipeline once globally
pipeline = KPipeline(lang_code='a') 

# 2. ADD THIS ROUTE to serve your webpage
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 'af_heart')
    
    if not text:
        return {"error": "No text provided"}, 400

    generator = pipeline(text, voice=voice, speed=1)
    
    audio_data = None
    for _, _, audio in generator:
        audio_data = audio
        break
    
    buf = io.BytesIO()
    sf.write(buf, audio_data, 24000, format='WAV')
    buf.seek(0)
    
    return send_file(buf, mimetype='audio/wav')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
