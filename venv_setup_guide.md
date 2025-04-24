# Complete Guide: Setting Up WRAITH Voice Assistant in a Virtual Environment

This guide will walk you through setting up a Python virtual environment on your Raspberry Pi and installing the WRAITH Voice Assistant from scratch.

## 1. Initial Setup on Raspberry Pi

First, update your Raspberry Pi system:

```bash
sudo apt update
sudo apt upgrade -y
```

Install required system dependencies that virtual environments will need:

```bash
sudo apt install -y python3-dev python3-pip portaudio19-dev libespeak-dev ffmpeg git
```
\
## 2. Create a Virtual Environment

Install the virtual environment package if you don't have it already:

```bash
sudo apt install -y python3-venv
```

Now create a project directory and a virtual environment inside it:

```bash
# Create a project directory
mkdir -p ~/wraith_assistant
cd ~/wraith_assistant

# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

Your command prompt should change to show `(venv)` at the beginning, indicating the virtual environment is active.

## 3. Transfer Project Files

There are several ways to get the project files onto your Raspberry Pi:

### Option A: Using SCP from your Windows machine

On your Windows computer, open PowerShell or Command Prompt and run:

```powershell
scp -r E:\FYP\respberry\* pi@RASPBERRY_PI_IP:~/wraith_assistant/
```

Replace `RASPBERRY_PI_IP` with your Raspberry Pi's IP address.

### Option B: Using Git (if your code is in a repository)

With your virtual environment activated on the Raspberry Pi:

```bash
cd ~/wraith_assistant
git clone https://github.com/YOUR_USERNAME/respberry.git .
```

### Option C: Direct download using Raspberry Pi browser

If your code is accessible via a web URL:

```bash
cd ~/wraith_assistant
wget https://your-code-url/archive/main.zip
unzip main.zip
rm main.zip
```

## 4. Install Python Dependencies in Virtual Environment

With your virtual environment still activated:

```bash
# Make sure pip is up to date
pip install --upgrade pip

# Install the required packages
pip install -r requirements.txt
```

If you encounter issues with specific packages, try installing them individually:

```bash
pip install SpeechRecognition
pip install pyaudio
pip install gTTS
pip install pygame
pip install pydub
pip install requests
pip install RPi.GPIO
```

## 5. Hardware Setup

Connect your hardware components:

1. Connect USB microphone to a USB port on your Raspberry Pi
2. Connect speakers via USB or the 3.5mm audio jack
3. (Optional) Connect an LED for visual feedback:
   - Connect the LED's anode (longer leg) to GPIO pin 4 through a 220-330 Ohm resistor
   - Connect the LED's cathode (shorter leg) to any GND pin

## 6. Configure Audio

Ensure your audio devices are properly recognized:

```bash
# List recording devices
arecord -l

# List playback devices
aplay -l
```

Test your microphone and speakers:

```bash
# Record 5 seconds of audio
arecord -d 5 test.wav

# Play it back
aplay test.wav
```

If needed, set default audio devices by creating/editing `/etc/asound.conf`:

```bash
sudo nano /etc/asound.conf
```

Add these contents (adjust card numbers based on your `arecord -l` output):

```
pcm.!default {
  type asym
  playback.pcm {
    type plug
    slave.pcm "hw:0,0"  # Replace with your speaker device
  }
  capture.pcm {
    type plug
    slave.pcm "hw:1,0"  # Replace with your microphone device
  }
}

ctl.!default {
  type hw
  card 0
}
```

## 7. Set Permissions

Make sure your user has permission to access audio and GPIO:

```bash
sudo usermod -a -G audio,gpio pi
```

You'll need to log out and log back in for these changes to take effect.

## 8. Run the Assistant

Make sure your virtual environment is activated:

```bash
cd ~/wraith_assistant
source venv/bin/activate
```

Make the script executable and run it:

```bash
chmod +x app.py
python app.py
```

You should now see the WRAITH Voice Assistant startup message and it will begin listening for voice commands.

## 9. Run at Startup (Optional)

To make the assistant start automatically when your Raspberry Pi boots:

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/wraith.service
```

Add the following content (adjust the paths to match your setup):

```
[Unit]
Description=WRAITH Voice Assistant
After=network.target sound.target

[Service]
ExecStart=/home/pi/wraith_assistant/venv/bin/python /home/pi/wraith_assistant/app.py
WorkingDirectory=/home/pi/wraith_assistant
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable wraith.service
sudo systemctl start wraith.service
```

Check the status to make sure it's running:

```bash
sudo systemctl status wraith.service
```

## Troubleshooting

### Audio Problems

If you have issues with audio detection:

```bash
# Check active audio devices
arecord -l
aplay -l

# Adjust audio levels
alsamixer
```

### Package Installation Issues

If you encounter issues installing packages:

```bash
# For PyAudio issues
sudo apt install -y portaudio19-dev
pip install pyaudio

# For pydub/ffmpeg issues
sudo apt install -y ffmpeg
```

### Virtual Environment Management

To deactivate the virtual environment when you're done:

```bash
deactivate
```

To reactivate it later:

```bash
cd ~/wraith_assistant
source venv/bin/activate
```

### Service Control

If you need to stop or restart the service:

```bash
sudo systemctl stop wraith.service    # Stop the service
sudo systemctl restart wraith.service # Restart the service
sudo systemctl disable wraith.service # Disable autostart
```

## Customization

To customize the assistant:
- Edit `app.py` to modify behavior or responses
- Adjust the LED settings in the code if needed
- Configure audio sensitivity by changing the `energy_threshold` parameter in the code 