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

        // Audio manager
        this.audioManager = null;

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
            numberImage: document.getElementById('number-image'),
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

            // Initialize audio manager
            if (!this.audioManager) {
                this.audioManager = new AudioManager();
                this.setupAudioCallbacks();

                // Add audio manager to window for debugging
                window.audioManager = this.audioManager;

                // Wait for audio manager to fully initialize
                setTimeout(() => {
                    console.log('🔊 Audio manager initialization complete');
                }, 1000);
            }
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

        // New Game Flow Events
        this.socket.on('play_audio', (data) => {
            console.log('🔊 Play audio request:', data);
            this.handlePlayAudio(data);
        });

        this.socket.on('play_audio_sequence', (data) => {
            console.log('🔊 Play audio sequence:', data);
            this.handlePlayAudioSequence(data);
        });

        this.socket.on('play_random_positive_feedback', (data) => {
            console.log('🎉 Play random positive feedback');
            this.handlePlayRandomPositiveFeedback();
        });

        this.socket.on('number_started', (data) => {
            console.log('🔢 Number started:', data);
            this.handleNumberStarted(data);
        });

        this.socket.on('game_completed', (data) => {
            console.log('🎉 Game completed:', data);
            this.handleGameCompleted(data);
        });

        this.socket.on('game_restarted', (data) => {
            console.log('🔄 Game restarted');
            this.handleGameRestarted();
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

        // Resume audio context on user interaction
        if (this.audioManager) {
            this.audioManager.resumeAudioContext();
        }

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

        // DO NOT update number display here - that shows the target number, not detected gesture
    }

    handleGestureLost(data) {
        // Reset gesture indicator
        this.elements.gestureIndicator.textContent = 'Show your hand!';
        this.elements.gestureIndicator.style.background = 'rgba(0, 0, 0, 0.7)'; // Back to black
    }

    // Audio Management
    setupAudioCallbacks() {
        if (!this.audioManager) return;

        // Set up audio finished callback
        this.audioManager.onAudioFinished = (audioFile) => {
            console.log(`🔊 Audio finished: ${audioFile}`);
            if (this.socket) {
                this.socket.emit('audio_finished', { file: audioFile });
            }
        };
    }

    // Game Flow Event Handlers
    async handlePlayAudio(data) {
        const audioFile = data.file;

        if (!this.audioManager) {
            console.warn('⚠️ Audio manager not initialized');
            return;
        }

        try {
            // Map backend file names to audio manager methods
            if (audioFile === 'hi_ready_to_play') {
                await this.audioManager.playGreeting();
            } else if (audioFile === 'show_me_your_fingers') {
                await this.audioManager.playShowFingers();
            } else if (audioFile === 'lets_start_counting') {
                await this.audioManager.playLetsStartCounting();
            } else if (audioFile.startsWith('number_')) {
                const number = parseInt(audioFile.split('_')[1]);
                await this.audioManager.playNumber(number);
            } else if (audioFile === 'try_again') {
                await this.audioManager.playTryAgain();
            }
        } catch (error) {
            console.error('❌ Audio playback error:', error);
        }
    }

    async handlePlayAudioSequence(data) {
        const sequence = data.sequence || [];

        for (const audioFile of sequence) {
            await this.handlePlayAudio({ file: audioFile });
            await this.audioManager.waitForAudioToFinish();

            // 2-second delay between audio files for clarity
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }

    async handlePlayRandomPositiveFeedback() {
        if (!this.audioManager) {
            console.warn('⚠️ Audio manager not initialized');
            return;
        }

        try {
            await this.audioManager.playRandomPositiveFeedback();
        } catch (error) {
            console.error('❌ Positive feedback audio error:', error);
        }
    }

    handleNumberStarted(data) {
        const number = data.number;
        const timeout = data.timeout;

        console.log(`🔢 Starting number ${number} with ${timeout}ms timeout`);

        // Update UI to show current number
        this.currentNumber = number;
        this.displayNumber(number);

        // Update phase
        this.currentPhase = 'counting_game';
        this.updateDebugInfo('phase', this.currentPhase);
        this.updateDebugInfo('number', number);

        // Show instruction
        this.elements.gestureIndicator.textContent = `Show me ${number} finger${number > 1 ? 's' : ''}!`;
    }

    handleGameCompleted(data) {
        console.log('🎉 Game completed!', data);

        // Show celebration
        this.elements.celebrationOverlay.classList.remove('hidden');

        // Update phase
        this.currentPhase = 'completed';
        this.updateDebugInfo('phase', this.currentPhase);

        // Reset number display
        this.elements.gestureIndicator.textContent = 'Congratulations! You counted to 5!';
    }

    handleGameRestarted() {
        console.log('🔄 Game restarted');

        // Hide celebration overlay
        this.elements.celebrationOverlay.classList.add('hidden');

        // Reset to setup phase
        this.currentPhase = 'setup';
        this.currentNumber = 1;

        // Show setup UI again
        document.body.classList.remove('video-active');
        this.elements.videoSection.classList.add('hidden');

        // Reset debug info
        this.updateDebugInfo('phase', this.currentPhase);
        this.updateDebugInfo('number', this.currentNumber);
        this.updateDebugInfo('gesture', 'None');
    }

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
        // Update number image source
        if (this.elements.numberImage) {
            this.elements.numberImage.src = `assets/images/${number}.png`;
            this.elements.numberImage.alt = `Number ${number}`;
            console.log(`📸 Updated number image to: ${number}.png`);
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

    restartGame() {
        console.log('🔄 Requesting game restart');
        if (this.socket) {
            this.socket.emit('restart_game', {});
        }
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