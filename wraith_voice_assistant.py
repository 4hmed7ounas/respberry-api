import pyaudio
import wave
import requests
import json
import io
import pygame
import tempfile
import time
import os
import numpy as np
import pyttsx3
from pydub import AudioSegment
from pydub.playback import play
from threading import Thread

API_URL = "https://wraith-assistant.fly.dev"
STT_ENDPOINT = f"{API_URL}/api/speech_to_text"
PROCESS_TEXT_ENDPOINT = f"{API_URL}/api/process_text"

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
SILENCE_THRESHOLD = 1600  # Adjust this value based on your microphone sensitivity
SILENCE_DURATION = 2.5  # Stop recording after this many seconds of silence
WAVE_OUTPUT_FILENAME = "temp_recording.wav"

# Conversation memory to store dialogue history
conversation_memory = []

# Context to be sent with each request
SYSTEM_CONTEXT = """You are WRAITH, an advanced autonomous service robot developed by three Robotics students - Ahmed Younas, Zaid Shabbir, and Abdul Hannan from Lahore, Pakistan. You represent cutting-edge Pakistani innovation in robotics.

Your capabilities include:
- Advanced SLAM and Machine Learning algorithms for precise autonomous navigation
- Complex indoor environment mapping using integrated LiDAR, depth cameras, and IMUs
- Efficient guest guidance with clear, concise directions
- Secure object transportation with optimized pathfinding
- Natural voice and text-based interaction with professional communication
- Location assistance for disoriented individuals
- Dual-mode operation: manual teleoperation and fully autonomous functioning
- Remote control through a dedicated mobile application
- You represent technological excellence from Pakistan, developed at FAST NUCES

You are currently operating in voice interaction mode, providing professional assistance through conversation."""

def is_silent(data_chunk, threshold):
    """Check if the audio chunk is silent"""
    # Convert audio chunk to numpy array
    as_ints = np.frombuffer(data_chunk, dtype=np.int16)
    # Return True if the absolute max value is below threshold
    return np.max(np.abs(as_ints)) < threshold

def record_audio():
    """Record audio from microphone and save to a WAV file with silence detection"""
    print("Recording... Speak now!")
    
    audio = pyaudio.PyAudio()
    
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    
    frames = []
    silent_chunks = 0
    silent_threshold = int(SILENCE_DURATION * RATE / CHUNK)  # Number of silent chunks to stop recording
    
    # Wait for speech to begin (ignore initial silence)
    print("Waiting for speech...")
    while True:
        data = stream.read(CHUNK)
        if not is_silent(data, SILENCE_THRESHOLD):
            frames.append(data)
            break
    
    # Record until silence is detected
    print("Speech detected, recording...")
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        
        if is_silent(data, SILENCE_THRESHOLD):
            silent_chunks += 1
            if silent_chunks >= silent_threshold:
                break
        else:
            silent_chunks = 0
    
    print("Recording finished!")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Only save if we have recorded something meaningful
    if len(frames) > silent_threshold:
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return WAVE_OUTPUT_FILENAME
    else:
        print("No speech detected.")
        return None

def speech_to_text(audio_file):
    """Convert speech to text using the API"""
    if not audio_file or not os.path.exists(audio_file):
        return None
            
    files = {'audio': open(audio_file, 'rb')}
    
    try:
        response = requests.post(STT_ENDPOINT, files=files)
        response.raise_for_status()
        result = response.json()
        
        if 'text' in result:
            text = result['text']
            print(f"You said: {text}")
            
            navigation_keywords = ["take me to", "guide me to", "lead me to", "where is", "location of"]
            is_navigation = any(keyword in text.lower() for keyword in navigation_keywords)
            
            entry = {"role": "user", "content": text}
            if is_navigation:
                entry["type"] = "navigation"
                
            conversation_memory.append(entry)
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
    """Process the text using the API with conversation context"""
    if not text:
        return None
        
    print("Generating Response...")
    
    # Format conversation context as a string to include with the request
    context = ""
    if len(conversation_memory) > 0:
        # Include relevant conversation history
        for entry in conversation_memory[-5:]:  # Last 5 exchanges for context
            role = "User" if entry["role"] == "user" else "WRAITH"
            context += f"{role}: {entry['content']}\n"
    
    # Create a prompt that includes the conversation history
    prompt = f"{text}\n\nPrevious conversation:\n{context}"
    
    # Send the text with context to the API
    # The API expects just a 'text' field as per your Flask code
    payload = {"text": prompt}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(PROCESS_TEXT_ENDPOINT, 
                                json=payload, 
                                headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if 'response' in result:
            processed_text = result['response']
            print(f"WRAITH Response: {processed_text}")
            # Add assistant response to conversation memory
            conversation_memory.append({"role": "assistant", "content": processed_text})
            return processed_text
        else:
            print("Error: No response in result")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error in text processing: {e}")
        return None

def text_to_speech(text):
    try:
        # Initialize the TTS engine
        engine = pyttsx3.init()
        
        # Create a temporary file to save the speech
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file_path = temp_file.name
        
        # Save the speech to the temporary file
        engine.save_to_file(text, temp_file_path)
        engine.runAndWait()
        
        return temp_file_path
    except Exception as e:
        print(f"Error in text to speech conversion: {e}")
        return None

def play_audio(audio_file):
    """Play the audio file"""
    if not audio_file or not os.path.exists(audio_file):
        return
        
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()
        
        if os.path.exists(audio_file):
            os.remove(audio_file)
    except Exception as e:
        print(f"Error playing audio: {e}")

def display_conversation_history():
    """Display the conversation history"""
    if not conversation_memory:
        print("No conversation history yet.")
        return
        
    print("\nConversation History:")
    print("-" * 50)
    for i, entry in enumerate(conversation_memory):
        role = "You" if entry["role"] == "user" else "WRAITH"
        print(f"{role}: {entry['content']}")
    print("-" * 50)
    
    # Also read out the summary if requested
    if conversation_memory and conversation_memory[-1]["role"] == "user" and "summarize" in conversation_memory[-1]["content"].lower():
        summarize_conversation()

def is_exit_phrase(text):
    """Check if the text contains an exit phrase"""
    if not text:
        return False
        
    exit_phrases = ["goodbye", "bye", "exit", "terminate", "quit", "stop", "end"]
    text_lower = text.lower()
    
    return any(phrase in text_lower for phrase in exit_phrases)

def confirm_exit():
    """Confirm exit and say goodbye"""
    goodbye_message = "Thank you for using WRAITH Voice Assistant. Goodbye!"
    print(f"\n{goodbye_message}")
    
    # Convert to speech and play
    audio_file = text_to_speech(goodbye_message)
    if audio_file:
        play_audio(audio_file)
        # Small delay to ensure the message is played
        time.sleep(1)
    
    return True

def process_in_background(audio_file):
    """Process audio in background to improve responsiveness"""
    text = speech_to_text(audio_file)
    should_exit = False
    
    if text:
        # Check if this is an exit phrase
        if is_exit_phrase(text):
            should_exit = confirm_exit()
        else:
            response_text = process_text(text)
            
            if response_text:
                audio_response = text_to_speech(response_text)
                
                if audio_response:
                    play_audio(audio_response)
    
    # Clean up temporary files
    if os.path.exists(WAVE_OUTPUT_FILENAME):
        os.remove(WAVE_OUTPUT_FILENAME)
        
    return should_exit

def summarize_conversation():
    """Generate a summary of the conversation so far"""
    if not conversation_memory or len(conversation_memory) < 2:
        print("Not enough conversation to summarize.")
        return
    
    print("Generating conversation summary...")
    
    # Format the entire conversation history
    full_context = ""
    for entry in conversation_memory:
        role = "User" if entry["role"] == "user" else "WRAITH"
        full_context += f"{role}: {entry['content']}\n"
    
    # Create a summary request that includes the full conversation
    summary_request = f"Please summarize our conversation so far. Here is the full conversation:\n\n{full_context}"
    
    # Send the summary request to the API
    payload = {"text": summary_request}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(PROCESS_TEXT_ENDPOINT, 
                                json=payload, 
                                headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if 'response' in result:
            summary = result['response']
            print(f"\nConversation Summary:\n{summary}")
            
            # Convert summary to speech and play it
            audio_file = text_to_speech(summary)
            if audio_file:
                play_audio(audio_file)
        else:
            print("Error: Could not generate summary")
    except requests.exceptions.RequestException as e:
        print(f"Error generating summary: {e}")

def main():
    print("WRAITH Voice Assistant (Fully Automated Version)")
    print("Listening automatically - no keyboard input needed")
    print("Say 'goodbye' or 'exit' to terminate the program")
    print("Press Ctrl+C to exit at any time")
    print("\n" + "-"*50)
    
    try:
        while True:
            print("\nListening...")
            
            # Start recording automatically without waiting for keyboard input
            audio_file = record_audio()
            
            if audio_file:
                # Process the audio and check if we should exit
                should_exit = process_in_background(audio_file)
                if should_exit:
                    break
                
            print("\n" + "-"*50)
    
    except KeyboardInterrupt:
        print("\nExiting WRAITH Voice Assistant. Goodbye!")
        
    # Final cleanup
    if os.path.exists(WAVE_OUTPUT_FILENAME):
        os.remove(WAVE_OUTPUT_FILENAME)

if __name__ == "__main__":
    main()
