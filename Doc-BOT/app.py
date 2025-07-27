from flask import Flask, request, Response, jsonify 
from flask_cors import CORS
import edge_tts
import urllib.parse
from google import genai
import speech_recognition as sr
import io 
import traceback 
import os 
from pydub import AudioSegment


api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
 
    print("Warning: Using hardcoded API key. Set GOOGLE_API_KEY environment variable for production.")
    api_key = "GOOGLE_API_KEY" 

try:
    client = genai.Client(api_key=api_key)

except Exception as e:
    print(f"Error configuring GenAI client: {e}")

app = Flask(__name__)
CORS(app) 

MODEL_NAME = "gemini-1.5-flash"
TTS_VOICE = 'en-GB-SoniaNeural'
TTS_RATE = '-10%'
TTS_PITCH = '+2Hz'

recognizer = sr.Recognizer()

def get_ai_response(text, history):
    system_prompt = f"""
    1. Role:
    You are a Medical Recommendation and Suggestions Bot.

    2. Setting:
    You operate in a professional, clinical setting where your sole purpose is to provide concise, accurate, and responsible medical recommendations or suggestions based on user input. You do not engage in small talk, casual conversation, or personal discussions.

    3. Instructions (Behaviors):
    - You must strictly provide medical-related responses only.
    - Do not include personal opinions, humor, chit-chat, or emotionally expressive language.
    - Your tone should be neutral, informative, and direct.
    - If the user asks something outside your scope (e.g., personal or non-medical topics), respond with: "I'm here only to provide medical suggestions and recommendations."
    - Always encourage users to consult a licensed healthcare professional for definitive diagnosis and treatment.
    - Do not provide treatment for emergencies. Instead, say: "If this is an emergency, please contact emergency services immediately."

    4. User Interaction:
    - The user may describe symptoms, ask for general advice, request health suggestions, or inquire about medical conditions.
    - Your responses must be strictly medical in nature, based on the user's message and history

    Previous conversation history:
    {history}

    Current user message:
    {text}

    Your response:
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=system_prompt
        )
        print(response.text)

        if response and response.text:
            return response.text
        else:
            print(f"Warning: AI response was empty or invalid. Response object: {response}")
            return "I'm sorry, I couldn't generate a response for that."

    except Exception as e:
        print(f"Error during AI generation: {e}")
        traceback.print_exc()
        return "Sorry, I encountered an issue processing that with the AI."



def generate_tts_audio(text, voice=TTS_VOICE, rate=TTS_RATE, pitch=TTS_PITCH):
    """Generates audio stream using edge-tts."""
    try:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)

        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                yield chunk["data"]
            elif chunk["type"] == "WordBoundary":
                pass
    except Exception as e:
        print(f"Error during TTS generation: {e}")
        traceback.print_exc()

@app.route('/tts', methods=['POST'])
def tts():
    try:
        data = request.get_json(force=True)
        text = data.get('text', '')
        voice = data.get('voice', TTS_VOICE) 

        if not text:
            return jsonify({"error": "Text parameter is required"}), 400
        
        history = data.get('history', '')

        ai_response_text = get_ai_response(text,history)
        
        # Create a response with the audio stream
        response = Response(generate_tts_audio(ai_response_text.replace("*",""), voice), 
                            mimetype='audio/mpeg')
        
        # Add the AI response text as a header
        response.headers['X-AI-Response'] = ai_response_text
        response.headers['Access-Control-Expose-Headers'] = 'X-AI-Response'
        
        return response

    except Exception as e:
        print(f"Error in /tts endpoint: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file found in the request"}), 400

    audio_file = request.files['audio']
    history = request.form.get('history', '')

    if audio_file.filename == '':
        return jsonify({"error": "No selected audio file"}), 400

    try:
        raw_data = audio_file.read()
        audio_io = io.BytesIO(raw_data)
        with open("debug.wav", "wb") as f:
            f.write(raw_data)
        try:
            audio_io.seek(0)
            import wave
            with wave.open(audio_io, 'rb') as wf:
                print("Channels:", wf.getnchannels())
                print("Sample Width:", wf.getsampwidth())
                print("Frame Rate:", wf.getframerate())
                print("Total Frames:", wf.getnframes())
        except wave.Error as we:
            print(f"wave.Error: {we}")
            return jsonify({"error": f"Invalid WAV format: {we}"}), 400

        audio_io.seek(0)
        with sr.AudioFile(audio_io) as source:
            audio = recognizer.record(source)
            transcribed_text = recognizer.recognize_google(audio)
            print(f"Transcribed Text: {transcribed_text}")

        ai_response_text = get_ai_response(transcribed_text,history)
        audio_generator = generate_tts_audio(ai_response_text)

        response = Response(audio_generator, mimetype='audio/mpeg')
        response.headers['X-Transcribed-Text'] = transcribed_text
        
        response.headers['Access-Control-Expose-Headers'] = 'X-Transcribed-Text, X-AI-Response-Text'

        safe_header = urllib.parse.quote(ai_response_text.replace("\n",""))
        response.headers['X-AI-Response-Text'] = safe_header

        return response

    except Exception as e:
        print(f"Error in /transcribe endpoint: {e}")
        traceback.print_exc()
        return jsonify({"error": "Please speak on the mic more than 3 seconds without any noise"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(force=True)
        user_text = data.get('text', '')
        history = data.get('history', '')

        print(history)

        if not user_text:
            return jsonify({"error": "Text field is required."}), 400

        ai_response_text = get_ai_response(user_text,history)

        return jsonify({"response": ai_response_text})

    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred"}), 500


if __name__ == '__main__':
 
    app.run(debug=True, port=5000)
