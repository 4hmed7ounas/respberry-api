# WRAITH Voice Assistant for Raspberry Pi

This project implements a voice communication system for Raspberry Pi that interacts with the WRAITH Assistant API. The system records audio from a microphone, converts it to text, processes the text, and plays back the response.

## Features

- Voice recording from microphone
- Speech-to-text conversion using the WRAITH API
- Text processing with Gemini AI
- Text-to-speech conversion
- Audio playback of responses

## Hardware Requirements

- Raspberry Pi (3B+ or newer recommended)
- USB microphone or USB sound card with microphone
- Speaker or headphones
- Internet connection

## Installation

1. Clone this repository to your Raspberry Pi:
   ```
   git clone https://github.com/4hmed7ounas/respberry-api.git
   cd respberry-api
   ```

2. Install the required system dependencies:
   ```
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-dev portaudio19-dev python3-pygame
   ```

3. Install the Python dependencies:
   ```
   pip3 install -r requirements.txt
   ```

4. Make the script executable:
   ```
   chmod +x wraith_voice_assistant.py
   ```

## Usage

1. Connect your microphone and speakers to the Raspberry Pi.

2. Run the voice assistant:
   ```
   python3 wraith_voice_assistant.py
   ```

3. Press Enter to start recording your voice.

4. Speak your query or command.

5. The system will process your speech and play back WRAITH's response.

6. Press Ctrl+C to exit the program.

## Troubleshooting

- If you encounter issues with audio recording, make sure your microphone is properly connected and recognized by the system. You can check connected audio devices with:
  ```
  arecord -l
  ```

- If you have issues with audio playback, check your speaker connections and volume settings.

- For network-related issues, ensure your Raspberry Pi has a stable internet connection.

## API Endpoints

The system interacts with the following API endpoints:

- Speech-to-Text: `https://wraith-assistant.fly.dev/api/speech_to_text`
- Text Processing: `https://wraith-assistant.fly.dev/api/process_text`
- Text-to-Speech: `https://wraith-assistant.fly.dev/api/text_to_speech`

## Contributors

- Ahmed Younas
- Zaid Shabbir
- Abdul Hannan
