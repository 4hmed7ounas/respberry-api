# Setting Up WRAITH Voice Assistant on Raspberry Pi 5

This guide will walk you through the steps to get your WRAITH Voice Assistant running on a Raspberry Pi 5.

## Hardware Setup

1. **Components needed:**
   - Raspberry Pi 5
   - USB Microphone
   - USB Speaker or Speaker connected via 3.5mm audio jack
   - LED (optional, for visual feedback)
   - 220-330 Ohm resistor (for LED)
   - Jumper wires

2. **LED Connection (Optional):**
   - Connect the LED's anode (longer leg) to GPIO pin 4 through a resistor
   - Connect the LED's cathode (shorter leg) to any GND pin

## Software Setup

### 1. Set Up Raspberry Pi OS

1. Install Raspberry Pi OS on an SD card using the Raspberry Pi Imager
2. Boot up your Raspberry Pi 5
3. Complete the initial setup (set locale, connect to WiFi, etc.)
4. Update the system:
```
sudo apt update
sudo apt upgrade -y
```

### 2. Configure Audio

1. Connect your USB microphone and speakers
2. Check that they are recognized:
```
arecord -l  # Lists recording devices
aplay -l    # Lists playback devices
```

3. Test the microphone:
```
arecord -d 5 test.wav  # Records 5 seconds of audio
aplay test.wav  # Plays it back
```

4. If needed, set default audio devices by creating/editing `/etc/asound.conf`:
```
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

### 3. Install Required Dependencies

1. Install system packages:
```
sudo apt install -y python3-pip python3-dev portaudio19-dev libespeak-dev ffmpeg
```

2. Clone the repository:
```
git clone https://github.com/YOUR_USERNAME/respberry.git
cd respberry
```

3. Install Python dependencies:
```
pip3 install -r requirements.txt
```

### 4. Run the Voice Assistant

1. Make the script executable:
```
chmod +x app.py
```

2. Run the voice assistant:
```
python3 app.py
```

3. **To run at startup (optional):**
   - Edit the system service file:
   ```
   sudo nano /etc/systemd/system/wraith.service
   ```
   
   - Add the following content:
   ```
   [Unit]
   Description=WRAITH Voice Assistant
   After=network.target sound.target

   [Service]
   ExecStart=/usr/bin/python3 /home/pi/respberry/app.py
   WorkingDirectory=/home/pi/respberry
   StandardOutput=inherit
   StandardError=inherit
   Restart=always
   User=pi

   [Install]
   WantedBy=multi-user.target
   ```

   - Enable and start the service:
   ```
   sudo systemctl enable wraith.service
   sudo systemctl start wraith.service
   ```

   - Check status:
   ```
   sudo systemctl status wraith.service
   ```

## Troubleshooting

### Audio Issues

1. **Microphone not working:**
   - Check connections
   - Run `arecord -l` to see if it's detected
   - Try another USB port
   - Adjust volume with `alsamixer`

2. **Speaker not working:**
   - Check connections
   - Run `aplay -l` to see if it's detected
   - Test with `aplay /usr/share/sounds/alsa/Front_Center.wav`
   - Adjust volume with `alsamixer`

3. **Permission issues:**
   - Make sure your user is in the audio group:
   ```
   sudo usermod -a -G audio pi
   ```

### GPIO Issues

If the LED doesn't work:
- Make sure RPi.GPIO is installed: `pip3 install RPi.GPIO`
- Check connections with a multimeter
- Try a different GPIO pin by changing the `LED_PIN` value in the code

### Speech Recognition Issues

If speech recognition is unreliable:
- Ensure you have a stable internet connection
- Try a higher quality microphone
- Adjust `energy_threshold` in the code to match your environment
- Speak clearly and at a consistent volume

## Further Customization

- Edit the `app.py` file to change the assistant's responses
- Adjust the LED brightness by modifying the duty cycle values
- Change the voice speed by modifying the speed factor in the code 