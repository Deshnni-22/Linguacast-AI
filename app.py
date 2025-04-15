from flask import Flask, request, jsonify, send_from_directory, render_template
from gtts import gTTS
import requests
import os
from pydub import AudioSegment

app = Flask(__name__)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

def translate_to_french(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": "fr",
        "dt": "t",
        "q": text
    }
    response = requests.get(url, params=params)
    result = response.json()
    return result[0][0][0]

def text_to_speech(text, lang, filename, slow=False):
    tts = gTTS(text=text, lang=lang, slow=slow)
    path = os.path.join(STATIC_DIR, filename)
    tts.save(path)
    return AudioSegment.from_mp3(path)

def generate_5_minute_podcast(english_text, french_text):
    podcast = AudioSegment.silent(duration=1000)

    # Minute 1–2: Intro
    intro = text_to_speech(
        f"Welcome! Let's learn a sentence. In English: {english_text}. In French: {french_text}.", 
        'en', 'intro.mp3')
    podcast += intro + AudioSegment.silent(duration=2000)

    # Minute 3–4: Repeat French slowly with pauses
    chunks = french_text.split()
    for word in chunks:
        part = text_to_speech(word, 'fr', f"{word}.mp3", slow=True)
        podcast += part + AudioSegment.silent(duration=2000)

    # Minute 5: Prompt user to speak
    closing = text_to_speech(
        "Now it's your turn! Try saying the full sentence out loud.", 'en', 'closing.mp3')
    podcast += closing + AudioSegment.silent(duration=10000)  # 10 sec pause

    output_path = os.path.join(STATIC_DIR, "five_minute_podcast.mp3")
    podcast.export(output_path, format="mp3")
    return "five_minute_podcast.mp3"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    english_text = data['sentence']
    french_text = translate_to_french(english_text)
    audio_file = generate_5_minute_podcast(english_text, french_text)

    return jsonify({
        "english": english_text,
        "french": french_text,
        "audio_path": f"/static/{audio_file}"
    })

@app.route('/static/<path:filename>')
def serve_audio(filename):
    return send_from_directory(STATIC_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
