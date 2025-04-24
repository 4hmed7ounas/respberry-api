#!/usr/bin/env python3
import time
import json
import threading
import requests
import os
import tempfile
import signal
import sys
from datetime import datetime
import wave
import pyaudio
import pygame
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

# Configuration
API_BASE_URL = 'https://wraith-assistant.fly.dev'
#API_BASE_URL = 'http://localhost:8080'

# Global state
is_recording = False
is_speaking = False
is_processing = False
chat_memory = []
running = True
assistant_active = True  # Always active by default

# GPIO setup for Raspberry Pi (only for LED feedback)
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    
    # Define GPIO pin for LED
    LED_PIN = 4
    
    # Setup LED pin
    GPIO.setup(LED_PIN, GPIO.OUT)
    
    # Initialize LED
    led_pwm = GPIO.PWM(LED_PIN, 100)
    led_pwm.start(0)
    
    has_gpio = True
    print("GPIO initialized successfully")
except ImportError:
    print("GPIO module not available. Running in development mode.")
    has_gpio = False

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 3000  # Adjust for sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0  # Seconds of silence to consider the end of a phrase
        
        # Initialize audio
        pygame.mixer.init()
        
        # Create temporary directory for audio files
        self.temp_dir = tempfile.mkdtemp()
        print(f"Temporary directory created at: {self.temp_dir}")
        
        # Start with greeting
        self.start_session()

    def continuous_listen(self):
        """Continuously listen for speech and process it when detected"""
        global is_recording, is_processing, assistant_active
        
        print("Starting continuous listening mode...")
        
        # Play startup sound to indicate ready
        self.play_sound("startup")
        
        # Start with welcome message/session
        if assistant_active:
            print("Assistant is active and ready")
        
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                print("Adjusting for ambient noise... Please be quiet")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Ambient noise profile adjusted")
                
                while running:
                    if is_processing or is_speaking:
                        time.sleep(0.1)
                        continue
                    
                    print("Listening for speech...")
                    
                    # Indicate listening state with LED
                    if has_gpio:
                        # Set LED to dim
                        led_pwm.ChangeDutyCycle(10)
                    
                    try:
                        # Listen for audio
                        is_recording = True
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                        is_recording = False
                        
                        # Visual indicator that speech was detected
                        if has_gpio:
                            # Brief flash to indicate detection
                            led_pwm.ChangeDutyCycle(100)
                            time.sleep(0.2)
                            led_pwm.ChangeDutyCycle(10)
                            
                        try:
                            # Recognize speech
                            text = self.recognizer.recognize_google(audio)
                            
                            if text:
                                print(f"Recognized: {text}")
                                
                                # Check for wake word/phrase if not already active
                                if not assistant_active and not any(wake_word in text.lower() for wake_word in ["hello", "hey wraith", "hi wraith"]):
                                    print("Wake word not detected, continuing to listen")
                                    continue
                                    
                                # Process the speech
                                self.process_input(text)
                            
                        except sr.UnknownValueError:
                            print("Could not understand audio")
                        except sr.RequestError as e:
                            print(f"Error with speech recognition service: {e}")
                    
                    except Exception as e:
                        print(f"Error in continuous listening: {e}")
                        is_recording = False
                        if has_gpio:
                            led_pwm.ChangeDutyCycle(0)
        
        except KeyboardInterrupt:
            print("Keyboard interrupt received")
        except Exception as e:
            print(f"Error in continuous listening: {e}")
        finally:
            is_recording = False
            if has_gpio:
                led_pwm.ChangeDutyCycle(0)

    def speak(self, text):
        global is_speaking
        
        if not text:
            return
            
        is_speaking = True
        print(f"Speaking: {text}")
        
        if has_gpio:
            # Pulse LED while speaking
            threading.Thread(target=self.pulse_led).start()
        
        try:
            # Create temporary file for TTS output
            temp_file = os.path.join(self.temp_dir, f"tts_{int(time.time())}.mp3")
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file)
            
            # Play the audio
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            # Delete the temporary file
            try:
                os.remove(temp_file)
            except:
                pass
                
        except Exception as e:
            print(f"Error during speech: {e}")
        finally:
            is_speaking = False
            # Turn off LED pulsing
            if has_gpio:
                led_pwm.ChangeDutyCycle(0)

    def format_chat_memory(self):
        if not chat_memory:
            return ""
        return "\n".join([f"{msg['role']}: {msg['text']}" for msg in chat_memory])

    def process_input(self, text):
        global is_processing, chat_memory
        
        if not text:
            return
            
        # Add user message to memory
        chat_memory.append({"role": "User", "text": text})
        print(f"User: {text}")
        
        is_processing = True
        
        # Indicate processing state with LED
        if has_gpio:
            led_pwm.ChangeDutyCycle(50)  # Medium brightness for processing
        
        try:
            # Play processing sound
            self.play_sound("processing")
            
            # Prepare request with context
            chat_context = self.format_chat_memory()
            input_with_context = f"{text}\n\nPrevious conversation:\n{chat_context}"
            
            # Make API request
            response = requests.post(
                f"{API_BASE_URL}/api/process_text",
                json={"text": input_with_context},
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get("response", "Sorry, I couldn't process that.")
                
                # Add assistant response to memory
                chat_memory.append({"role": "WRAITH", "text": response_text})
                print(f"WRAITH: {response_text}")
                
                # Speak the response
                self.speak(response_text)
            else:
                error_msg = "Sorry, I encountered an error processing your request."
                print(f"API Error: {response.status_code} - {response.text}")
                self.speak(error_msg)
        except Exception as e:
            print(f"Error processing input: {e}")
            self.speak("Sorry, I encountered an error processing your request.")
        finally:
            is_processing = False
            # Return to standby LED state (dim)
            if has_gpio and running:
                led_pwm.ChangeDutyCycle(10)

    def start_session(self):
        global chat_memory
        
        # Clear chat memory
        chat_memory = []
        
        # Play startup sound
        self.play_sound("startup")
        
        welcome_msg = "Initializing WRAITH system. I am your autonomous service robot assistant designed for navigation, guidance, and transportation tasks. How may I assist you today?"
        
        # Add welcome message to memory
        chat_memory.append({"role": "WRAITH", "text": welcome_msg})
        
        print("WRAITH: " + welcome_msg)
        self.speak(welcome_msg)

    def play_sound(self, sound_type):
        """Generate and play different sound effects"""
        
        duration = 0.5  # seconds
        sample_rate = 44100  # Hz
        
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=sample_rate,
                        output=True)
        
        # Generate different sounds based on type
        if sound_type == "startup":
            # Rising tone
            samples = []
            for i in range(int(sample_rate * duration)):
                t = i / sample_rate  # Time in seconds
                freq = 300 + 700 * (t / duration)  # Rising from 300Hz to 1000Hz
                amplitude = 0.1 * (1 - t / duration)  # Fading out
                sample = amplitude * float(9 * (t % (1/freq))/(1/freq) - 1)
                samples.append(sample)
                
        elif sound_type == "shutdown":
            # Falling tone
            samples = []
            for i in range(int(sample_rate * duration)):
                t = i / sample_rate
                freq = 800 - 600 * (t / duration)  # Falling from 800Hz to 200Hz
                amplitude = 0.1 * (1 - t / duration)  # Fading out
                sample = amplitude * float(9 * (t % (1/freq))/(1/freq) - 1)
                samples.append(sample)
                
        elif sound_type == "processing":
            # Short beep
            duration = 0.1  # Shorter duration for processing sound
            samples = []
            freq = 440  # Hz
            for i in range(int(sample_rate * duration)):
                t = i / sample_rate
                amplitude = 0.05 * (1 - t / duration)  # Fading out
                sample = amplitude * float(t * freq % 1 < 0.5)  # Square wave
                samples.append(sample)
        
        # Convert samples to the correct format for PyAudio
        import array
        import struct
        
        # Convert list of floats to a byte array
        samples_array = array.array('f', samples)
        samples_bytes = samples_array.tobytes()
        
        # Play the sound
        stream.write(samples_bytes)
        
        # Close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

    def pulse_led(self):
        """Pulse the LED while speaking"""
        if not has_gpio:
            return
            
        while is_speaking:
            for dc in range(10, 101, 5):
                led_pwm.ChangeDutyCycle(dc)
                time.sleep(0.05)
            for dc in range(100, 9, -5):
                led_pwm.ChangeDutyCycle(dc)
                time.sleep(0.05)

    def cleanup(self):
        """Clean up resources"""
        if has_gpio:
            GPIO.cleanup()
        
        # Remove temporary directory
        try:
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)
        except:
            pass

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    global running
    print("\nShutting down...")
    running = False
    time.sleep(1)
    sys.exit(0)

def main():
    global running
    
    # Display startup message
    print("\n" + "="*50)
    print("WRAITH Voice Assistant for Raspberry Pi")
    print("="*50 + "\n")
    
    # Initialize assistant
    assistant = VoiceAssistant()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Start continuous listening in the main thread
        assistant.continuous_listen()
    
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        # Clean up
        assistant.cleanup()
        print("Voice assistant shutdown completed")

if __name__ == "__main__":
    main()
