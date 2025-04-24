# WRAITH Voice Assistant for Raspberry Pi

A voice-controlled assistant designed for Raspberry Pi 5 that provides navigation, guidance, and transportation assistance.

## Hardware Requirements

- Raspberry Pi 5 (or compatible)
- USB Microphone
- Speaker (USB or 3.5mm audio jack)
- LED connected to GPIO pin (optional for visual feedback)

## GPIO Connection Setup

- LED: GPIO 4 (optional for visual feedback)

## Installation

1. Clone this repository:
```
git clone <your-repository-url>
cd respberry
```

2. Install required dependencies:
```
pip install -r requirements.txt
```

3. On Raspberry Pi, you may need to install some additional system dependencies for audio:
```
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio
```

## Usage

### Running the Assistant

```
python app.py
```

The assistant will automatically:
1. Initialize with a welcome message
2. Begin listening for voice input
3. Process voice commands when detected
4. Respond with voice output

### Voice Interaction

The assistant continuously listens for voice input:
1. When you speak, it will detect your voice
2. When you pause, it will process your command
3. It will respond via voice and continue listening

The LED will provide visual feedback:
- Dim light when actively listening
- Brief flash when speech is detected
- Medium brightness when processing
- Pulsing when speaking
- Returns to dim when ready for next input

### Control Keys

- Press Ctrl+C to exit the application

## Features

- Continuous voice detection and processing
- Voice recognition using Google Speech Recognition
- Text-to-speech output
- LED visual feedback
- Sound effects for different actions
- Conversation memory
- Integration with the WRAITH Assistant API

## Troubleshooting

- If you have issues with audio input/output, check your device configuration:
  ```
  arecord -l  # List recording devices
  aplay -l    # List playback devices
  ```

- Adjust the microphone sensitivity in the code if needed (see `energy_threshold` parameter in the `VoiceAssistant` class)

- For permission issues with GPIO pins, make sure to run the script with sudo:
  ```
  sudo python app.py
  ```

## License

[Your License Information] 