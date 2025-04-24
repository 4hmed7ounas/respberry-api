# Transferring the WRAITH Voice Assistant to Raspberry Pi 5

Here are several methods to transfer your code from your development machine to your Raspberry Pi 5.

## Method 1: Using Git

If you're already using Git for version control:

1. **On your development machine:**
   - Push your code to GitHub or another Git service:
   ```
   git add .
   git commit -m "Ready for Raspberry Pi deployment"
   git push origin main
   ```

2. **On your Raspberry Pi:**
   - Clone the repository:
   ```
   git clone https://github.com/YOUR_USERNAME/respberry.git
   cd respberry
   ```

## Method 2: Using SCP (Secure Copy)

1. **Find your Raspberry Pi's IP address:**
   - On the Raspberry Pi, run:
   ```
   hostname -I
   ```
   - This will return something like `192.168.1.100`

2. **On your Windows development machine:**
   - Open PowerShell or Command Prompt
   - Navigate to your project directory:
   ```
   cd E:\FYP\respberry
   ```
   - Transfer all files to the Raspberry Pi:
   ```
   scp -r * pi@192.168.1.100:/home/pi/respberry/
   ```
   - Replace `192.168.1.100` with your Pi's actual IP address
   - You'll be prompted for the Pi user's password

## Method 3: Using a USB Drive

1. **On your development machine:**
   - Copy all files to a USB drive
   
2. **On your Raspberry Pi:**
   - Insert the USB drive
   - Mount it (usually happens automatically)
   - Copy files to your home directory:
   ```
   mkdir -p ~/respberry
   cp -r /media/pi/USB_DRIVE_NAME/* ~/respberry/
   ```

## Method 4: Using Visual Studio Code Remote Development

1. **Install the Remote Development extension in VS Code**

2. **Configure SSH on your Raspberry Pi:**
   - Ensure SSH is enabled (use `sudo raspi-config`)
   - Note down the IP address (`hostname -I`)

3. **In VS Code:**
   - Press F1 and select "Remote-SSH: Connect to Host..."
   - Enter `pi@192.168.1.100` (replace with your Pi's IP)
   - VS Code will connect to your Pi
   - You can now open folders, edit files, and use the integrated terminal

4. **Deploy your project:**
   - In VS Code, open the Explorer view
   - Drag and drop your local files to the remote file explorer
   - Or use the integrated terminal to clone your Git repository

## Method 5: Using Syncthing for Continuous Synchronization

If you want to keep your development machine and Raspberry Pi in sync:

1. **Install Syncthing on both devices:**
   - On Windows: Download from syncthing.net
   - On Raspberry Pi:
   ```
   sudo apt install syncthing
   sudo systemctl enable syncthing@pi
   sudo systemctl start syncthing@pi
   ```

2. **Configure Syncthing:**
   - Access the web UI on your Pi at: `http://localhost:8384/`
   - Add your development folder as a shared folder
   - On your Windows machine, accept the shared folder
   - Files will automatically stay in sync between both devices

## After Transfer

Once you've transferred the files to your Raspberry Pi:

1. **Set file permissions:**
   ```
   chmod +x app.py
   ```

2. **Install dependencies:**
   ```
   pip3 install -r requirements.txt
   ```

3. **Run the application:**
   ```
   python3 app.py
   ```

Refer to the `raspberry_setup.md` file for complete setup instructions and troubleshooting. 