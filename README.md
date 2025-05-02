# WRAITH Voice Assistant for Raspberry Pi 5

A voice assistant implementation for Raspberry Pi 5 that uses a USB microphone for input and USB speakers for output. This project is based on the WRAITH assistant concept and connects to a remote API for speech-to-text and text-to-speech processing.

## Features

- Voice input via USB microphone
- Voice output via USB speakers
- Web interface for interaction
- Command-line interface for headless operation
- Chat memory to maintain conversation context
- Theme toggle (light/dark mode)
- Responsive design

## Requirements

- Raspberry Pi 5 (4GB RAM)
- USB Microphone
- USB Speakers
- Python 3.7+
- Internet connection (for API access)

## Installation on Raspberry Pi 5

1. Clone the repository:
```bash
git clone https://github.com/yourusername/respberry.git
cd respberry
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Install system dependencies for PyAudio and text-to-speech:
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
sudo apt-get install espeak espeak-data libespeak-dev
```

## Configuration

You can configure the API endpoint by creating a `.env` file in the project root:

```
API_BASE_URL=https://wraith-assistant.fly.dev
```

## Usage

### Command Line Interface

Run the assistant in command-line mode:

```bash
python app.py
```

This will start the voice assistant in the terminal. Speak when prompted and say "exit" or "quit" to end the session.

### Web Interface

Run the assistant as a web application:

```bash
python app.py --web
```

Then open a browser and navigate to `http://localhost:5000` or `http://[raspberry-pi-ip]:5000` from another device on the same network.

## Raspberry Pi Setup Tips

### Audio Configuration

1. List available audio devices:
```bash
aplay -l  # List playback devices
arecord -l  # List recording devices
```

2. Set default audio devices by creating/editing `/etc/asound.conf`:
```
pcm.!default {
  type asym
  playback.pcm {
    type plug
    slave.pcm "hw:0,0"  # Replace with your USB speaker device
  }
  capture.pcm {
    type plug
    slave.pcm "hw:1,0"  # Replace with your USB microphone device
  }
}
```


defaults.pcm.card 2
defaults.pcm.device 0
defaults.ctl.card 2

3. Test audio recording:
```bash
arecord -d 5 -f cd test.wav  # Record 5 seconds
aplay test.wav  # Play back recording
```

### Autostart on Boot

To make the voice assistant start automatically on boot:

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/wraith.service
```

2. Add the following content:
```
[Unit]
Description=WRAITH Voice Assistant
After=network.target

[Service]
ExecStart=/home/pi/respberry/venv/bin/python /home/pi/respberry/app.py
WorkingDirectory=/home/pi/respberry
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable wraith.service
sudo systemctl start wraith.service
```

## Troubleshooting

### Microphone Issues

If the microphone isn't working:
- Check if the microphone is properly connected
- Verify it's recognized with `arecord -l`
- Test recording with `arecord -d 5 test.wav`
- Adjust microphone volume with `alsamixer`

### Speaker Issues

If the speakers aren't working:
- Check if speakers are properly connected
- Verify they're recognized with `aplay -l`
- Test playback with `aplay /usr/share/sounds/alsa/Front_Center.wav`
- Adjust volume with `alsamixer`

## License

MIT
