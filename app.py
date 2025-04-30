from flask import Flask, request, jsonify, send_from_directory, render_template
from gtts import gTTS
import requests
import os
from pydub import AudioSegment

app = Flask(__name__)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Translate English to selected language using Google Translate API
def translate_text(text, target_lang):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": target_lang,
        "dt": "t",
        "q": text
    }
    response = requests.get(url, params=params)
    result = response.json()
    return result[0][0][0]

# Convert text to speech using gTTS
def text_to_speech(text, lang, filename, slow=False):
    tts = gTTS(text=text, lang=lang, slow=slow)
    path = os.path.join(STATIC_DIR, filename)
    tts.save(path)
    return AudioSegment.from_mp3(path)

# Generate a 5-minute podcast
def generate_5_minute_podcast(english_text, translated_text, lang_code):
    podcast = AudioSegment.silent(duration=1000)

    # Minute 1–2: Introduction
    intro_text = f"Welcome! Let's learn a sentence. In English: {english_text}. In {lang_code}: {translated_text}."
    intro_audio = text_to_speech(intro_text, 'en', "intro.mp3")
    podcast += intro_audio + AudioSegment.silent(duration=2000)

    # Minute 3–4: Slow repetition with pauses
    words = translated_text.split()
    for word in words:
        part_audio = text_to_speech(word, lang_code, f"{word}.mp3", slow=True)
        podcast += part_audio + AudioSegment.silent(duration=2000)

    # Minute 5: Prompt for user practice
    closing_text = "Now it's your turn! Try saying the full sentence out loud."
    closing_audio = text_to_speech(closing_text, 'en', "closing.mp3")
    podcast += closing_audio + AudioSegment.silent(duration=10000)

    # Save final podcast
    output_path = os.path.join(STATIC_DIR, "five_minute_podcast.mp3")
    podcast.export(output_path, format="mp3")
    return "five_minute_podcast.mp3"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    english_text = data['sentence']
    target_lang = data['language']

    translated_text = translate_text(english_text, target_lang)
    audio_file = generate_5_minute_podcast(english_text, translated_text, target_lang)

    return jsonify({
        "english": english_text,
        "translation": translated_text,
        "audio_path": f"/static/{audio_file}"
    })

@app.route('/static/<path:filename>')
def serve_audio(filename):
    return send_from_directory(STATIC_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)

