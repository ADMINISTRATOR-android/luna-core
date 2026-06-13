from flask import Flask, request, send_file, send_from_directory
import io
import os

# Initialize Flask
app = Flask(__name__, static_folder='static')

# We declare the variable but do not load the model yet
pipeline = None

def get_pipeline():
    global pipeline
    if pipeline is None:
        print("Loading Kokoro model into memory...")
        from kokoro import KPipeline
        # This will only happen on the first request to /synthesize
        pipeline = KPipeline(lang_code='a')
    return pipeline

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/synthesize', methods=['POST'])
def synthesize():
    # Model loads only when a user actually requests audio
    local_pipeline = get_pipeline()
    
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 'af_heart')
    
    if not text:
        return {"error": "No text provided"}, 400

    generator = local_pipeline(text, voice=voice, speed=1)
    
    # Generate audio
    audio_data = None
    for _, _, audio in generator:
        audio_data = audio
        break
    
    buf = io.BytesIO()
    import soundfile as sf
    sf.write(buf, audio_data, 24000, format='WAV')
    buf.seek(0)
    
    return send_file(buf, mimetype='audio/wav')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
