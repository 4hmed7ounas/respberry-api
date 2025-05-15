#!/usr/bin/env python3
import pyaudio
import wave
import requests
import json
import io
import pygame
import tempfile
import time
import os
from pydub import AudioSegment
from pydub.playback import play

# API Configuration
API_URL = "https://wraith-assistant.fly.dev"
STT_ENDPOINT = f"{API_URL}/api/speech_to_text"
PROCESS_TEXT_ENDPOINT = f"{API_URL}/api/process_text"
TTS_ENDPOINT = f"{API_URL}/api/text_to_speech"

# Audio Recording Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5  # Adjust as needed
WAVE_OUTPUT_FILENAME = "temp_recording.wav"

def record_audio():
    """Record audio from microphone and save to a WAV file"""
    print("Recording... Speak now!")
    
    audio = pyaudio.PyAudio()
    
    # Open audio stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    
    frames = []
    
    # Record audio in chunks
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("Recording finished!")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save the recorded audio as WAV file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return WAVE_OUTPUT_FILENAME

def speech_to_text(audio_file):
    """Convert speech to text using the API"""
    print("Converting speech to text...")
    
    files = {'audio': open(audio_file, 'rb')}
    
    try:
        response = requests.post(STT_ENDPOINT, files=files)
        response.raise_for_status()
        result = response.json()
        
        if 'text' in result:
            text = result['text']
            print(f"You said: {text}")
            return text
        else:
            print("Error: No text in response")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error in speech to text conversion: {e}")
        return None
    finally:
        files['audio'].close()

def process_text(text):
    """Process the text using the API"""
    print("Processing text...")
    
    payload = {"text": text}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(PROCESS_TEXT_ENDPOINT, 
                                json=payload, 
                                headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if 'response' in result:
            processed_text = result['response']
            print(f"WRAITH response: {processed_text}")
            return processed_text
        else:
            print("Error: No response in result")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error in text processing: {e}")
        return None

def text_to_speech(text):
    """Convert text to speech using the API"""
    print("Converting text to speech...")
    
    payload = {"text": text}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(TTS_ENDPOINT, 
                                json=payload, 
                                headers=headers)
        response.raise_for_status()
        
        # Save the audio response to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        return temp_file_path
    except requests.exceptions.RequestException as e:
        print(f"Error in text to speech conversion: {e}")
        return None

def play_audio(audio_file):
    """Play the audio file"""
    print("Playing audio response...")
    
    try:
        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()
        
        # Clean up the temporary file
        if os.path.exists(audio_file):
            os.remove(audio_file)
    except Exception as e:
        print(f"Error playing audio: {e}")

def main():
    print("WRAITH Voice Assistant")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            print("\nPress Enter to start recording (or Ctrl+C to exit)...")
            input()
            
            # Record audio
            audio_file = record_audio()
            
            # Convert speech to text
            text = speech_to_text(audio_file)
            
            if text:
                # Process the text
                response_text = process_text(text)
                
                if response_text:
                    # Convert response text to speech
                    audio_response = text_to_speech(response_text)
                    
                    if audio_response:
                        # Play the audio response
                        play_audio(audio_response)
            
            # Clean up the temporary recording file
            if os.path.exists(WAVE_OUTPUT_FILENAME):
                os.remove(WAVE_OUTPUT_FILENAME)
                
            print("\n" + "-"*50)
    
    except KeyboardInterrupt:
        print("\nExiting WRAITH Voice Assistant. Goodbye!")

if __name__ == "__main__":
    main()
