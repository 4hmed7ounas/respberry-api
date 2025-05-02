#!/usr/bin/env python3
import os
import wave
import json
import time
import pyaudio
import requests
import threading
import numpy as np
import speech_recognition as sr
import pyttsx3
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://wraith-assistant.fly.dev')
# API_BASE_URL = 'http://localhost:8080'

# Initialize Flask app
app = Flask(__name__)

# Global variables
is_recording = False
is_speaking = False
is_processing = False
chat_memory = []
use_custom_stt = True  # Set to True to use our custom speech-to-text API
use_server_tts = True  # Set to True to use server-side text-to-speech

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Initialize speech recognition
recognizer = sr.Recognizer()

# Initialize text-to-speech engine
try:
    engine = pyttsx3.init()
    
    # Set up a male voice if available
    voices = engine.getProperty('voices')
    for voice in voices:
        if "male" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    tts_available = True
except Exception as e:
    print(f"Warning: Could not initialize pyttsx3: {e}")
    print("Text-to-speech will use alternative methods")
    engine = None
    tts_available = False

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/start_session', methods=['POST'])
def start_session():
    global chat_memory
    chat_memory = []
    welcome_message = "Initializing WRAITH system. I am your autonomous service robot. How may I assist you today?"
    
    # Add to chat memory
    chat_memory.append({
        'role': 'WRAITH',
        'text': welcome_message
    })
    
    # Speak the welcome message
    threading.Thread(target=speak_text, args=(welcome_message,)).start()
    
    return jsonify({'status': 'success', 'message': welcome_message})

@app.route('/api/end_session', methods=['POST'])
def end_session():
    global chat_memory
    chat_memory = []
    farewell_message = "Terminating assistance protocol."
    
    # Speak the farewell message
    threading.Thread(target=speak_text, args=(farewell_message,)).start()
    
    return jsonify({'status': 'success', 'message': farewell_message})

@app.route('/api/record', methods=['POST'])
def record_audio():
    global is_recording, is_processing
    
    if is_recording or is_processing:
        return jsonify({'status': 'error', 'message': 'Already recording or processing'})
    
    try:
        is_recording = True
        
        # Record audio
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        
        print("Recording...")
        frames = []
        
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("Recording finished")
        
        stream.stop_stream()
        stream.close()
        
        # Save the recorded audio to a WAV file
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        is_recording = False
        is_processing = True
        
        # Process the recorded audio
        if use_custom_stt:
            text = custom_speech_to_text()
        else:
            text = speech_to_text()
        
        # Add to chat memory
        chat_memory.append({
            'role': 'User',
            'text': text
        })
        
        # Process the user input
        response = process_user_input(text)
        
        is_processing = False
        
        return jsonify({'status': 'success', 'text': text, 'response': response})
    
    except Exception as e:
        is_recording = False
        is_processing = False
        return jsonify({'status': 'error', 'message': str(e)})

def speech_to_text():
    """Convert speech to text using SpeechRecognition library"""
    try:
        with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"Error in speech recognition: {e}")
        return "Sorry, I couldn't understand that."

def custom_speech_to_text():
    """Convert speech to text using custom API"""
    try:
        with open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
            files = {'audio': (WAVE_OUTPUT_FILENAME, audio_file, 'audio/wav')}
            response = requests.post(f"{API_BASE_URL}/api/speech_to_text", files=files)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('text', "Sorry, I couldn't understand that.")
            else:
                print(f"API Error: {response.status_code}")
                return "Sorry, I couldn't understand that."
    except Exception as e:
        print(f"Error in custom speech recognition: {e}")
        return "Sorry, I couldn't understand that."

def process_user_input(text):
    """Process user input and get a response"""
    try:
        # Format chat memory
        chat_context = format_chat_memory()
        input_with_context = f"{text}\n\nPrevious conversation:\n{chat_context}"
        
        # Send to API
        response = requests.post(
            f"{API_BASE_URL}/api/process_text",
            json={"text": input_with_context}
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', "I'm sorry, I couldn't process that.")
            
            # Add to chat memory
            chat_memory.append({
                'role': 'WRAITH',
                'text': response_text
            })
            
            # Speak the response
            threading.Thread(target=speak_text, args=(response_text,)).start()
            
            return response_text
        else:
            error_message = "I'm sorry, there was an error processing your request."
            
            # Add to chat memory
            chat_memory.append({
                'role': 'WRAITH',
                'text': error_message
            })
            
            # Speak the error message
            threading.Thread(target=speak_text, args=(error_message,)).start()
            
            return error_message
    
    except Exception as e:
        error_message = f"Error: {str(e)}"
        
        # Add to chat memory
        chat_memory.append({
            'role': 'WRAITH',
            'text': error_message
        })
        
        # Speak the error message
        threading.Thread(target=speak_text, args=(error_message,)).start()
        
        return error_message

def format_chat_memory():
    """Format chat memory into a string"""
    return '\n'.join([f"{msg['role']}: {msg['text']}" for msg in chat_memory])

def speak_text(text):
    """Speak the given text"""
    global is_speaking
    
    if is_speaking:
        return
    
    is_speaking = True
    
    try:
        if use_server_tts:
            server_side_tts(text)
        elif tts_available and engine:
            engine.say(text)
            engine.runAndWait()
        else:
            # Fallback to command-line espeak if pyttsx3 is not available
            try:
                import subprocess
                subprocess.run(['espeak', text])
            except Exception as e:
                print(f"Error using espeak command line: {e}")
                print(f"Text (not spoken): {text}")
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        print(f"Text (not spoken): {text}")
    finally:
        is_speaking = False

def server_side_tts(text):
    """Use server-side text-to-speech"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/text_to_speech",
            json={"text": text}
        )
        
        if response.status_code == 200:
            # Save the audio to a file
            with open("tts_output.wav", "wb") as f:
                f.write(response.content)
            
            # Play the audio
            play_audio("tts_output.wav")
        else:
            # Fallback to local TTS
            engine.say(text)
            engine.runAndWait()
    
    except Exception as e:
        print(f"Error in server-side TTS: {e}")
        # Fallback to local TTS
        engine.say(text)
        engine.runAndWait()

def play_audio(file_path):
    """Play an audio file"""
    try:
        # Open the audio file
        wf = wave.open(file_path, 'rb')
        
        # Open a stream
        stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
        
        # Read data in chunks
        data = wf.readframes(CHUNK)
        
        # Play the audio
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)
        
        # Close everything
        stream.stop_stream()
        stream.close()
    
    except Exception as e:
        print(f"Error playing audio: {e}")

def main():
    """Main function to run the assistant from command line"""
    print("WRAITH Voice Assistant")
    print("Say 'exit' or 'quit' to end the session")
    
    # Start welcome message
    welcome_message = "Initializing WRAITH system. I am your autonomous service robot. How may I assist you today?"
    print(f"WRAITH: {welcome_message}")
    speak_text(welcome_message)
    
    # Main loop
    while True:
        try:
            print("\nListening...")
            
            # Record audio
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
            
            frames = []
            
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Save the recorded audio to a WAV file
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Process the recorded audio
            if use_custom_stt:
                text = custom_speech_to_text()
            else:
                text = speech_to_text()
            
            print(f"You said: {text}")
            
            # Check for exit command
            if text.lower() in ['exit', 'quit', 'goodbye']:
                farewell_message = "Terminating assistance protocol."
                print(f"WRAITH: {farewell_message}")
                speak_text(farewell_message)
                break
            
            # Add to chat memory
            chat_memory.append({
                'role': 'User',
                'text': text
            })
            
            # Process the user input
            response = process_user_input(text)
            print(f"WRAITH: {response}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    # Clean up
    audio.terminate()
    print("Session ended.")

if __name__ == '__main__':
    # Check if running as a web app or command line
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--web':
        # Run as web app
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        # Run as command line app
        main()