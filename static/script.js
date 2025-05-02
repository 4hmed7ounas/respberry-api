// DOM elements
const chatContainer = document.getElementById('chatContainer');
const statusElement = document.getElementById('status');
const startButton = document.getElementById('startButton');
const recordButton = document.getElementById('recordButton');
const endButton = document.getElementById('endButton');
const themeToggle = document.getElementById('themeToggle');
const backgroundAnimation = document.getElementById('backgroundAnimation');
const typingIndicator = document.getElementById('typingIndicator');
const htmlElement = document.documentElement;

// Chat memory
let chatMemory = [];

// Initialize the app
function initApp() {
    createBackgroundElements();
    setupEventListeners();
    checkLocalStorage();
    
    // Clear welcome message after 5 seconds
    setTimeout(() => {
        const welcomeAnimation = document.querySelector('.welcome-animation');
        if (welcomeAnimation) {
            welcomeAnimation.style.opacity = '0';
            setTimeout(() => {
                welcomeAnimation.remove();
            }, 500);
        }
    }, 5000);
}

// Create background elements
function createBackgroundElements() {
    // Clear existing elements
    backgroundAnimation.innerHTML = '';
    
    // Create circuit-like circles
    for (let i = 0; i < 15; i++) {
        const circuit = document.createElement('div');
        circuit.classList.add('circuit');
        
        const size = Math.random() * 200 + 50;
        const posX = Math.random() * window.innerWidth;
        const posY = Math.random() * window.innerHeight;
        
        circuit.style.width = `${size}px`;
        circuit.style.height = `${size}px`;
        circuit.style.left = `${posX}px`;
        circuit.style.top = `${posY}px`;
        
        backgroundAnimation.appendChild(circuit);
    }
    
    // Create grid lines
    for (let i = 0; i < 8; i++) {
        const line = document.createElement('div');
        line.classList.add('grid-line');
        
        const isHorizontal = Math.random() > 0.5;
        if (isHorizontal) {
            line.style.width = '100%';
            line.style.height = '1px';
            line.style.top = `${Math.random() * 100}%`;
            line.style.left = '0';
        } else {
            line.style.width = '1px';
            line.style.height = '100%';
            line.style.left = `${Math.random() * 100}%`;
            line.style.top = '0';
        }
        
        backgroundAnimation.appendChild(line);
    }
}

// Set up event listeners
function setupEventListeners() {
    // Theme toggle
    themeToggle.addEventListener('click', toggleTheme);
    
    // Button click handlers
    startButton.addEventListener('click', startSession);
    endButton.addEventListener('click', endSession);
    
    // Record button
    recordButton.addEventListener('mousedown', startRecording);
    recordButton.addEventListener('mouseup', stopRecording);
    recordButton.addEventListener('mouseleave', stopRecording);
    
    // Touch events for mobile
    recordButton.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startRecording();
    });
    
    recordButton.addEventListener('touchend', (e) => {
        e.preventDefault();
        stopRecording();
    });
    
    // Window resize
    window.addEventListener('resize', createBackgroundElements);
}

// Toggle theme
function toggleTheme() {
    const currentTheme = htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    htmlElement.setAttribute('data-theme', newTheme);
    
    // Update icon
    themeToggle.innerHTML = newTheme === 'light' ? 
        '<i class="fas fa-moon"></i>' : 
        '<i class="fas fa-sun"></i>';
    
    // Save preference
    localStorage.setItem('theme', newTheme);
}

// Check local storage for saved preferences
function checkLocalStorage() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        htmlElement.setAttribute('data-theme', savedTheme);
        themeToggle.innerHTML = savedTheme === 'light' ? 
            '<i class="fas fa-moon"></i>' : 
            '<i class="fas fa-sun"></i>';
    }
}

// Start session
function startSession() {
    showTypingIndicator(true);
    statusElement.textContent = 'Starting session...';
    
    fetch('/api/start_session', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        showTypingIndicator(false);
        const messageElement = addMessage(data.message, 'wraith');
        startButton.disabled = true;
        recordButton.disabled = false;
        endButton.disabled = false;
        statusElement.textContent = 'Press and hold to speak';
        
        // Clear chat memory
        chatMemory = [];
        
        // Add to chat memory
        chatMemory.push({
            role: 'WRAITH',
            text: data.message
        });
    })
    .catch(error => {
        console.error('Error starting session:', error);
        showTypingIndicator(false);
        statusElement.textContent = `Error: ${error.message}`;
    });
}

// End session
function endSession() {
    showTypingIndicator(true);
    statusElement.textContent = 'Ending session...';
    
    fetch('/api/end_session', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        showTypingIndicator(false);
        const messageElement = addMessage(data.message, 'wraith');
        startButton.disabled = false;
        recordButton.disabled = true;
        endButton.disabled = true;
        statusElement.textContent = 'Session ended. Press "Start Interaction" to begin again';
        
        // Clear chat memory
        chatMemory = [];
    })
    .catch(error => {
        console.error('Error ending session:', error);
        showTypingIndicator(false);
        statusElement.textContent = `Error: ${error.message}`;
    });
}

// Start recording
function startRecording() {
    if (recordButton.disabled) return;
    
    recordButton.classList.add('recording');
    statusElement.textContent = 'Listening... Speak now';
    recordButton.querySelector('.mic-waves').style.display = 'block';
}

// Stop recording
function stopRecording() {
    if (!recordButton.classList.contains('recording')) return;
    
    recordButton.classList.remove('recording');
    statusElement.textContent = 'Processing your speech...';
    recordButton.querySelector('.mic-waves').style.display = 'none';
    
    showTypingIndicator(true);
    
    fetch('/api/record', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Add user message
            addMessage(data.text, 'user');
            
            // Add to chat memory
            chatMemory.push({
                role: 'User',
                text: data.text
            });
            
            // Add assistant response
            showTypingIndicator(false);
            const messageElement = addMessage(data.response, 'wraith');
            
            // Add to chat memory
            chatMemory.push({
                role: 'WRAITH',
                text: data.response
            });
            
            statusElement.textContent = 'Press and hold to speak';
        } else {
            throw new Error(data.message);
        }
    })
    .catch(error => {
        console.error('Error recording:', error);
        showTypingIndicator(false);
        statusElement.textContent = `Error: ${error.message}`;
    });
}

// Toggle typing indicator
function showTypingIndicator(show) {
    if (show) {
        typingIndicator.classList.remove('hidden');
        statusElement.classList.add('hidden');
    } else {
        typingIndicator.classList.add('hidden');
        statusElement.classList.remove('hidden');
    }
}

// Add message to chat
function addMessage(text, sender) {
    // Remove welcome animation if it exists
    const welcomeAnimation = document.querySelector('.welcome-animation');
    if (welcomeAnimation) {
        welcomeAnimation.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'wraith-message');
    
    if (sender !== 'user') {
        const robotIcon = document.createElement('div');
        robotIcon.classList.add('robot-icon');
        robotIcon.innerHTML = '<i class="fas fa-robot"></i>';
        messageDiv.appendChild(robotIcon);
    }
    
    const messageText = document.createElement('div');
    messageText.classList.add('message-text');
    messageText.textContent = text;
    messageDiv.appendChild(messageText);
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);
