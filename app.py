from flask import Flask, request, send_file
from kokoro import KPipeline
import soundfile as sf
import io
import os

app = Flask(__name__)

# Initialize pipeline once globally for performance
# 'a' = American English; 'b' = British English
pipeline = KPipeline(lang_code='a') 

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 'af_heart') # Default to 'af_heart'
    
    if not text:
        return {"error": "No text provided"}, 400

    # Kokoro pipeline generation
    generator = pipeline(text, voice=voice, speed=1)
    
    # We grab the first audio output generated
    audio_data = None
    for _, _, audio in generator:
        audio_data = audio
        break
    
    # Write audio to an in-memory buffer to avoid disk I/O
    buf = io.BytesIO()
    sf.write(buf, audio_data, 24000, format='WAV')
    buf.seek(0)
    
    return send_file(buf, mimetype='audio/wav')

if __name__ == '__main__':
    # Render/Railway will override the port via environment variables
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
  
