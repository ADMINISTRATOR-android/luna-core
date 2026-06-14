import os
from flask import Flask, request, send_file
from piper.voice import PiperVoice

app = Flask(__name__)

# Ensure your model files are in the 'model' folder
MODEL_PATH = "model/en_US-amy-medium.onnx"
CONFIG_PATH = "model/en_US-amy-medium.onnx.json"

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()
    text = data.get("text", "")
    
    if not text:
        return "No text provided", 400

    output_file = "output.wav"
    
    # Load the voice engine. 
    # Because Piper uses ONNX, this is very RAM-friendly.
    voice = PiperVoice.load(MODEL_PATH, config_path=CONFIG_PATH)
    
    # Synthesize directly to a file
    with open(output_file, "wb") as f:
        voice.synthesize(text, f)
    
    # Send the file and let Flask handle closing the file
    return send_file(output_file, mimetype="audio/wav")

if __name__ == '__main__':
    # Render provides the port via an environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
