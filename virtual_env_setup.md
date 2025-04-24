# Setting Up WRAITH Voice Assistant in a Virtual Environment

Since you already have a virtual environment set up on your Raspberry Pi, follow these steps to integrate the WRAITH Voice Assistant.

## 1. Activate Your Virtual Environment

First, make sure your virtual environment is activated:

```bash
# Navigate to your virtual environment location (if needed)
cd /path/to/your/venv/directory

# Activate the virtual environment
source bin/activate   # On Linux/Raspberry Pi
```

Your command prompt should change to indicate the virtual environment is active.

## 2. Transfer Project Files

Transfer the project files to your Raspberry Pi using one of the methods from `transfer_to_pi.md`. For example, using SCP:

```bash
# On your Windows machine
scp -r E:\FYP\respberry\* pi@192.168.1.100:/path/to/your/project/
```

Or if you prefer to use Git:

```bash
# On your Raspberry Pi (with venv activated)
cd /path/to/your/project
git clone https://github.com/YOUR_USERNAME/respberry.git .
# Note the dot at the end to clone into the current directory
```

## 3. Install Dependencies in Your Virtual Environment

With your virtual environment still activated, install the required packages:

```bash
# Make sure you're in the project directory
cd /path/to/your/project

# Install dependencies
pip install -r requirements.txt
```

## 4. Hardware Setup

Connect your hardware as described in the `raspberry_setup.md` file:
- Connect your USB microphone
- Connect your speaker (USB or 3.5mm)
- (Optional) Connect an LED to GPIO pin 4 with a resistor

## 5. Configure Audio

Follow the audio configuration steps from `raspberry_setup.md`:

```bash
# Check audio devices
arecord -l
aplay -l

# Test microphone
arecord -d 5 test.wav
aplay test.wav
```

If needed, configure ALSA as described in the main setup guide.

## 6. Run the Assistant

With your virtual environment activated, run the application:

```bash
# Make sure the script is executable
chmod +x app.py

# Run the application
python app.py
```

## 7. Automate Startup (Optional)

To run the assistant at startup while using your virtual environment, modify the systemd service:

```bash
sudo nano /etc/systemd/system/wraith.service
```

Add the following, replacing paths with your actual paths:

```
[Unit]
Description=WRAITH Voice Assistant
After=network.target sound.target

[Service]
ExecStart=/path/to/your/venv/bin/python /path/to/your/project/app.py
WorkingDirectory=/path/to/your/project
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl enable wraith.service
sudo systemctl start wraith.service
```

## Troubleshooting Virtual Environment Issues

### Package Installation Problems

If you encounter package installation issues:

```bash
# Update pip
pip install --upgrade pip

# Install individual packages with verbose output
pip install SpeechRecognition -v
pip install RPi.GPIO -v
```

### System Dependencies

Some packages require system-level dependencies even when using virtual environments:

```bash
# Install required system packages
sudo apt install -y portaudio19-dev libespeak-dev ffmpeg
```

### Permissions for GPIO and Audio

Virtual environments may need additional permissions:

```bash
# Add your user to the GPIO and audio groups
sudo usermod -a -G gpio,audio pi

# Log out and log back in for changes to take effect
```

### PyAudio Issues

If PyAudio installation fails:

```bash
# Install system dependencies
sudo apt install -y python3-dev portaudio19-dev

# Install PyAudio
pip install pyaudio
```

## Deactivating the Virtual Environment

When you're done working with the assistant, you can deactivate the virtual environment:

```bash
deactivate
```

This returns you to the system Python environment. 