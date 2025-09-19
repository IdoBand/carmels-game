// Toddler Counting Game - WebSocket Client

class GameClient {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentPhase = 'setup';
        this.currentNumber = 1;
        this.gameState = {};

        // DOM elements
        this.elements = {};
        this.initializeElements();

        // Event handlers
        this.setupEventHandlers();

        // Connection settings
        this.serverUrl = window.location.origin;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;

        console.log('🎮 GameClient initialized');
    }

    initializeElements() {
        // Cache all DOM elements
        this.elements = {
            // Status elements
            statusText: document.getElementById('status-text'),
            statusDot: document.getElementById('status-dot'),

            // Avatar elements
            avatarFace: document.getElementById('avatar-face'),
            avatarMessage: document.getElementById('avatar-message'),
            speechBubble: document.getElementById('avatar-speech-bubble'),

            // Video elements
            videoSection: document.getElementById('video-section'),
            videoFeed: document.getElementById('video-feed'),
            gestureIndicator: document.getElementById('gesture-indicator'),

            // Game content elements
            numberDisplay: document.getElementById('number-display'),
            currentNumber: document.getElementById('current-number'),
            numberDots: document.getElementById('number-dots'),
            mainInstruction: document.getElementById('main-instruction'),
            subInstruction: document.getElementById('sub-instruction'),

            // Progress elements
            progressSection: document.getElementById('progress-section'),
            progressFill: document.getElementById('progress-fill'),
            progressText: document.getElementById('progress-text'),

            // Camera setup elements
            cameraSetup: document.getElementById('camera-setup'),
            testCamerasBtn: document.getElementById('test-cameras-btn'),
            cameraList: document.getElementById('camera-list'),
            cameraOptions: document.getElementById('camera-options'),
            startGameBtn: document.getElementById('start-game-btn'),

            // Overlay elements
            celebrationOverlay: document.getElementById('celebration-overlay'),
            playAgainBtn: document.getElementById('play-again-btn'),
            errorModal: document.getElementById('error-modal'),
            errorMessage: document.getElementById('error-message'),
            dismissErrorBtn: document.getElementById('dismiss-error-btn'),

            // Debug elements
            debugPanel: document.getElementById('debug-panel'),
            debugPhase: document.getElementById('debug-phase'),
            debugNumber: document.getElementById('debug-number'),
            debugGesture: document.getElementById('debug-gesture'),
            debugConnection: document.getElementById('debug-connection')
        };

        console.log('📋 DOM elements initialized');
    }

    setupEventHandlers() {
        // Camera setup buttons
        this.elements.testCamerasBtn.addEventListener('click', () => this.testCameras());
        this.elements.startGameBtn.addEventListener('click', () => this.startGame());

        // Game control buttons
        this.elements.playAgainBtn.addEventListener('click', () => this.restartGame());
        this.elements.dismissErrorBtn.addEventListener('click', () => this.dismissError());

        console.log('🎛️ Event handlers setup complete');
    }

    connect() {
        console.log(`🔌 Connecting to server at ${this.serverUrl}`);

        try {
            this.socket = io(this.serverUrl, {
                timeout: 5000,
                forceNew: true
            });

            this.setupSocketEventHandlers();

        } catch (error) {
            console.error('❌ Connection failed:', error);
            this.handleConnectionError(error);
        }
    }

    setupSocketEventHandlers() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('✅ Connected to server');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus('connected', 'Connected to game server');
            this.updateDebugInfo('connection', 'Connected');
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from server');
            this.isConnected = false;
            this.updateConnectionStatus('error', 'Disconnected from server');
            this.updateDebugInfo('connection', 'Disconnected');
        });

        this.socket.on('connect_error', (error) => {
            console.error('❌ Connection error:', error);
            this.handleConnectionError(error);
        });

        // Server status
        this.socket.on('server_status', (data) => {
            console.log('📡 Server status:', data);
            this.updateAvatarMessage(data.message || 'Server is ready!');
        });

        // Camera events
        this.socket.on('camera_list', (data) => {
            console.log('📹 Available cameras:', data.cameras);
            this.displayAvailableCameras(data.cameras);
        });

        this.socket.on('camera_status', (data) => {
            console.log('📹 Camera status:', data);
            if (data.status === 'started') {
                this.onCameraStarted(data);
            } else if (data.status === 'error') {
                this.showError(`Camera error: ${data.message}`);
            }
        });

        // Gesture detection events
        this.socket.on('gesture_detected', (data) => {
            console.log('🤖 Gesture detected:', data);
            this.handleGestureDetected(data);
            this.updateDebugInfo('gesture', `${data.number} (${data.confidence.toFixed(2)})`);
        });

        this.socket.on('gesture_lost', (data) => {
            console.log('👋 Gesture lost');
            this.handleGestureLost(data);
            this.updateDebugInfo('gesture', 'None');
        });

        // Game flow events (these will be implemented in Phase 3)
        this.socket.on('game_phase_changed', (data) => {
            console.log('🎮 Game phase changed:', data);
            this.handlePhaseChange(data);
        });

        this.socket.on('number_success', (data) => {
            console.log('✅ Number success:', data);
            this.handleNumberSuccess(data);
        });

        this.socket.on('next_number', (data) => {
            console.log('➡️ Next number:', data);
            this.handleNextNumber(data);
        });

        console.log('📡 Socket event handlers setup complete');
    }

    // Camera Management
    testCameras() {
        console.log('🔍 Testing cameras...');
        this.updateAvatarMessage('Let me find your camera...');
        this.elements.testCamerasBtn.disabled = true;

        if (this.socket) {
            this.socket.emit('request_camera_test', {});
        }
    }

    displayAvailableCameras(cameras) {
        const optionsContainer = this.elements.cameraOptions;
        optionsContainer.innerHTML = '';

        if (cameras.length === 0) {
            optionsContainer.innerHTML = '<p>No cameras found. Please check your camera connection.</p>';
            this.updateAvatarMessage('Oh no! I couldn\'t find any cameras. Please check your camera!');
            return;
        }

        cameras.forEach((camera, index) => {
            const option = document.createElement('div');
            option.className = 'camera-option';
            option.innerHTML = `
                <input type="radio" name="camera" value="${camera.index}" id="camera-${camera.index}">
                <label for="camera-${camera.index}">
                    <strong>${camera.name}</strong> (${camera.resolution})
                </label>
            `;

            option.addEventListener('click', () => {
                // Select this camera option
                const radioBtn = option.querySelector('input[type="radio"]');
                radioBtn.checked = true;

                // Update visual selection
                document.querySelectorAll('.camera-option').forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');

                // Enable start button
                this.elements.startGameBtn.classList.remove('hidden');
            });

            optionsContainer.appendChild(option);

            // Auto-select first camera
            if (index === 0) {
                option.click();
            }
        });

        this.elements.cameraList.classList.remove('hidden');
        this.elements.testCamerasBtn.disabled = false;
        this.updateAvatarMessage(`Great! I found ${cameras.length} camera${cameras.length > 1 ? 's' : ''}. Pick one and let's play!`);
    }

    startGame() {
        const selectedCamera = document.querySelector('input[name="camera"]:checked');
        if (!selectedCamera) {
            this.showError('Please select a camera first!');
            return;
        }

        const cameraIndex = parseInt(selectedCamera.value);
        console.log(`🚀 Starting game with camera ${cameraIndex}`);

        this.updateAvatarMessage('Starting the camera... Get ready to count!');
        this.elements.startGameBtn.disabled = true;

        if (this.socket) {
            this.socket.emit('start_camera', { camera_index: cameraIndex });
        }
    }

    onCameraStarted(data) {
        console.log('✅ Camera started successfully');

        // Start video feed
        this.startVideoFeed();

        // Switch to video mode - hide all setup UI and show full screen video
        document.body.classList.add('video-active');
        this.elements.videoSection.classList.remove('hidden');

        // Update game state
        this.currentPhase = 'waiting_for_start';
        this.updateDebugInfo('phase', this.currentPhase);

        console.log('📹 Switched to full-screen video mode');
    }

    startVideoFeed() {
        // Start the video feed from the backend
        const videoUrl = `${window.location.origin}/video_feed`;
        this.elements.videoFeed.src = videoUrl;
        console.log('📹 Starting video feed from:', videoUrl);
    }

    // Gesture Handling
    handleGestureDetected(data) {
        const number = data.number;
        const confidence = data.confidence;

        // Update gesture indicator with real-time feedback
        this.elements.gestureIndicator.textContent = `${number} finger${number > 1 ? 's' : ''} detected!`;
        this.elements.gestureIndicator.style.background = 'rgba(81, 207, 102, 0.8)'; // Green

        // Update number display
        this.displayNumber(number);
    }

    handleGestureLost(data) {
        // Reset gesture indicator
        this.elements.gestureIndicator.textContent = 'Show your hand!';
        this.elements.gestureIndicator.style.background = 'rgba(0, 0, 0, 0.7)'; // Back to black
    }

    // Removed all game logic as requested

    // UI Update Methods
    updateConnectionStatus(status, message) {
        this.elements.statusText.textContent = message;
        this.elements.statusDot.className = `status-dot ${status}`;
    }

    updateAvatarMessage(message) {
        this.elements.avatarMessage.textContent = message;

        // Add animation
        this.elements.speechBubble.classList.add('fade-in');
        setTimeout(() => {
            this.elements.speechBubble.classList.remove('fade-in');
        }, 500);
    }

    displayNumber(number) {
        this.elements.currentNumber.textContent = number;

        // Create dots for visual representation
        const dotsContainer = this.elements.numberDots;
        dotsContainer.innerHTML = '';

        // Limit dots to avoid overwhelming display (max 10)
        const dotCount = Math.min(number, 10);
        for (let i = 0; i < dotCount; i++) {
            const dot = document.createElement('div');
            dot.className = 'dot';
            dot.style.animationDelay = `${i * 0.1}s`;
            dotsContainer.appendChild(dot);
        }
    }

    updateProgress(percentage) {
        const completed = Math.floor((percentage / 100) * 10);
        this.elements.progressFill.style.width = `${percentage}%`;
        this.elements.progressText.textContent = `${completed} / 10`;
    }

    updateDebugInfo(key, value) {
        if (this.elements[`debug${key.charAt(0).toUpperCase() + key.slice(1)}`]) {
            this.elements[`debug${key.charAt(0).toUpperCase() + key.slice(1)}`].textContent = value;
        }
    }

    // Error Handling
    handleConnectionError(error) {
        console.error('❌ Connection error:', error);
        this.updateConnectionStatus('error', 'Connection failed');

        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);

            console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
            setTimeout(() => this.connect(), delay);
        } else {
            this.showError('Unable to connect to the game server. Please refresh the page and try again.');
        }
    }

    showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorModal.classList.remove('hidden');
    }

    dismissError() {
        this.elements.errorModal.classList.add('hidden');
    }

    // Utility Methods
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }

    getGameState() {
        return {
            isConnected: this.isConnected,
            currentPhase: this.currentPhase,
            currentNumber: this.currentNumber,
            gameState: this.gameState
        };
    }
}

// Export for use in other scripts
window.GameClient = GameClient;