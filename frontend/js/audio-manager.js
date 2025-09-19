// Audio Manager for Toddler Counting Game

class AudioManager {
    constructor() {
        // Audio context and settings
        this.audioContext = null;
        this.masterVolume = 1;
        this.effectsVolume = 0.6;

        // Audio file paths - matching actual file structure
        this.audioBasePath = '/assets/audio/';
        this.audioFiles = {
            numbers: {
                1: 'numbers/one.mp3',
                2: 'numbers/two.mp3',
                3: 'numbers/three.mp3',
                4: 'numbers/four.mp3',
                5: 'numbers/five.mp3'
            },
            greetings: {
                hi_ready_to_play: 'greetings/hi_ready_to_play.mp3'
            },
            instructions: {
                show_me_your_fingers: 'instructions/show_me_your_fingers.mp3',
                lets_start_counting: 'instructions/lets_start_counting.mp3'
            },
            positive_feedback: [
                'positive_feedback/correct.mp3',
                'positive_feedback/eze_yofi.mp3',
                'positive_feedback/great_kol_hakavod.mp3'
            ],
            encouragement: {
                try_again: 'encouragement/try_again.mp3',
                try_again_c: 'encouragement/try_again_c.mp3'
            }
        };


        // Audio cache
        this.audioCache = new Map();
        this.loadingPromises = new Map();


        // State
        this.isInitialized = false;
        this.isMuted = false;

        this.initialize();
    }

    async initialize() {
        console.log('🔊 Initializing Audio Manager...');

        try {
            // Initialize Web Audio API context
            await this.initializeAudioContext();

            // Try to preload critical audio files
            await this.preloadCriticalAudio();

            this.isInitialized = true;
            console.log('✅ Audio Manager initialized successfully');

        } catch (error) {
            console.warn('⚠️ Audio initialization error:', error);
            this.isInitialized = true;
        }
    }

    async initializeAudioContext() {
        // Create audio context (user gesture required)
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

            // Handle suspended context (Chrome policy)
            if (this.audioContext.state === 'suspended') {
                console.log('🔊 Audio context suspended, will resume on user interaction');

                // Resume on any user interaction
                const resumeContext = async () => {
                    if (this.audioContext.state === 'suspended') {
                        await this.audioContext.resume();
                        console.log('🔊 Audio context resumed');
                    }
                    document.removeEventListener('click', resumeContext);
                    document.removeEventListener('touchstart', resumeContext);
                };

                document.addEventListener('click', resumeContext);
                document.addEventListener('touchstart', resumeContext);
            }
        }
    }


    async preloadCriticalAudio() {
        // Preload the most important audio files
        const criticalFiles = [
            this.audioFiles.greetings.hi_ready_to_play,
            this.audioFiles.instructions.show_me_your_fingers,
            this.audioFiles.numbers[1],
            this.audioFiles.numbers[2],
            this.audioFiles.numbers[3]
        ];

        const preloadPromises = criticalFiles.map(file => this.loadAudio(file, false));

        try {
            await Promise.allSettled(preloadPromises);
            console.log('✅ Critical audio files preloaded');
        } catch (error) {
            console.warn('⚠️ Some audio files failed to preload:', error);
        }
    }

    // Audio Loading and Playback
    async loadAudio(filename, playImmediately = false) {
        const fullPath = this.audioBasePath + filename;
        console.log(`🔊 Loading audio: ${fullPath}`);
        console.log(`🔊 Absolute URL: ${new URL(fullPath, window.location.origin).href}`);

        // Check cache
        if (this.audioCache.has(fullPath)) {
            console.log(`✅ Audio found in cache: ${fullPath}`);
            const audio = this.audioCache.get(fullPath);
            if (playImmediately) {
                return this.playAudio(audio);
            }
            return audio;
        }

        // Check if already loading
        if (this.loadingPromises.has(fullPath)) {
            const audio = await this.loadingPromises.get(fullPath);
            if (playImmediately) {
                return this.playAudio(audio);
            }
            return audio;
        }

        // Start loading
        const loadPromise = new Promise((resolve, reject) => {
            const audio = new Audio(fullPath);

            audio.addEventListener('canplaythrough', () => {
                this.audioCache.set(fullPath, audio);
                this.loadingPromises.delete(fullPath);
                resolve(audio);
            });

            audio.addEventListener('error', (error) => {
                console.error(`❌ Failed to load audio: ${fullPath}`, error);
                console.error(`❌ Audio error details:`, {
                    code: audio.error?.code,
                    message: audio.error?.message,
                    src: audio.src,
                    networkState: audio.networkState,
                    readyState: audio.readyState
                });
                this.loadingPromises.delete(fullPath);
                reject(error);
            });

            audio.load();
        });

        this.loadingPromises.set(fullPath, loadPromise);

        try {
            const audio = await loadPromise;
            if (playImmediately) {
                return this.playAudio(audio);
            }
            return audio;
        } catch (error) {
            // Audio file failed to load, will use speech synthesis instead
            console.warn(`⚠️ Audio file not available: ${filename}`);
            throw error;
        }
    }

    async playAudio(audioElement) {
        if (this.isMuted || !audioElement) return;

        try {
            // Resume audio context if needed
            await this.resumeAudioContext();

            audioElement.volume = this.effectsVolume * this.masterVolume;
            audioElement.currentTime = 0;

            // Set up onended callback to trigger audio finished event
            const onEnded = () => {
                console.log(`🔊 Audio ended: ${audioElement.src}`);
                audioElement.removeEventListener('ended', onEnded);

                // Call the callback if it exists
                if (this.onAudioFinished) {
                    this.onAudioFinished(audioElement.src);
                }
            };

            audioElement.addEventListener('ended', onEnded);
            await audioElement.play();

            return audioElement;
        } catch (error) {
            console.warn('⚠️ Audio playback error:', error);
            if (error.name === 'NotAllowedError') {
                console.warn('⚠️ Audio requires user interaction. Audio context suspended.');
            }
            throw error;
        }
    }


    // High-Level Audio Methods for Game Flow
    async playGreeting() {
        console.log('🔊 Playing greeting: hi_ready_to_play');

        // Wait for audio manager initialization if needed
        while (!this.isInitialized) {
            console.log('⏳ Waiting for audio manager initialization...');
            await new Promise(resolve => setTimeout(resolve, 100));
        }

        try {
            await this.loadAudio(this.audioFiles.greetings.hi_ready_to_play, true);
            console.log('✅ Successfully played greeting MP3');
        } catch (error) {
            console.error('❌ Greeting MP3 failed:', error);
            console.error('❌ Full path attempted:', this.audioBasePath + this.audioFiles.greetings.hi_ready_to_play);
            // DO NOT fallback to speech synthesis - we want to use the MP3 file
            throw error;
        }
    }

    async playShowFingers() {
        console.log('🔊 Playing instruction: show_me_your_fingers');

        try {
            await this.loadAudio(this.audioFiles.instructions.show_me_your_fingers, true);
            console.log('✅ Successfully played show fingers MP3');
        } catch (error) {
            console.error('❌ Show fingers MP3 failed:', error);
            console.error('❌ Full path attempted:', this.audioBasePath + this.audioFiles.instructions.show_me_your_fingers);
            // DO NOT fallback to speech synthesis - we want to use the MP3 file
            throw error;
        }
    }

    async playLetsStartCounting() {
        console.log('🔊 Playing instruction: lets_start_counting');

        try {
            await this.loadAudio(this.audioFiles.instructions.lets_start_counting, true);
            console.log('✅ Successfully played lets start counting MP3');
        } catch (error) {
            console.error('❌ Lets start counting MP3 failed:', error);
            console.error('❌ Full path attempted:', this.audioBasePath + this.audioFiles.instructions.lets_start_counting);
            // DO NOT fallback to speech synthesis - we want to use the MP3 file
            throw error;
        }
    }

    async playNumber(number) {
        console.log(`🔊 Playing number: ${number}`);

        try {
            const audioFile = this.audioFiles.numbers[number];
            if (audioFile) {
                await this.loadAudio(audioFile, true);
                console.log(`✅ Successfully played number ${number} MP3`);
            } else {
                throw new Error(`Audio file not configured for number ${number}`);
            }
        } catch (error) {
            console.error(`❌ Number ${number} MP3 failed:`, error);
            if (this.audioFiles.numbers[number]) {
                console.error('❌ Full path attempted:', this.audioBasePath + this.audioFiles.numbers[number]);
            }
            // DO NOT fallback to speech synthesis - we want to use the MP3 file
            throw error;
        }
    }

    async playRandomPositiveFeedback() {
        console.log('🔊 Playing random positive feedback');

        try {
            const feedbackFiles = this.audioFiles.positive_feedback;
            const randomIndex = Math.floor(Math.random() * feedbackFiles.length);
            const selectedFile = feedbackFiles[randomIndex];

            console.log(`🎉 Selected feedback: ${selectedFile}`);
            await this.loadAudio(selectedFile, true);
        } catch (error) {
            console.error('❌ Random positive feedback failed:', error);
            throw error;
        }
    }

    async playTryAgain() {
        console.log('🔊 Playing encouragement: try_again');

        try {
            await this.loadAudio(this.audioFiles.encouragement.try_again, true);
        } catch (error) {
            console.error('❌ Try again MP3 failed:', error);
            throw error;
        }
    }



    // Utility Methods
    getNumberText(number) {
        const numberWords = {
            1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
            6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten'
        };
        return numberWords[number] || number.toString();
    }

    // Volume and Settings Control
    setMasterVolume(volume) {
        this.masterVolume = Math.max(0, Math.min(1, volume));
        console.log(`🔊 Master volume set to: ${this.masterVolume}`);
    }


    setEffectsVolume(volume) {
        this.effectsVolume = Math.max(0, Math.min(1, volume));
        console.log(`🎵 Effects volume set to: ${this.effectsVolume}`);
    }

    toggleMute() {
        this.isMuted = !this.isMuted;
        console.log(`🔊 Audio ${this.isMuted ? 'muted' : 'unmuted'}`);
        return this.isMuted;
    }

    // User Interaction Methods (for touch/click events)
    async resumeAudioContext() {
        if (this.audioContext && this.audioContext.state === 'suspended') {
            try {
                await this.audioContext.resume();
                console.log('🔊 Audio context resumed by user interaction');
            } catch (error) {
                console.warn('⚠️ Failed to resume audio context:', error);
            }
        }
    }

    // Test Methods
    async testAudio() {
        console.log('🧪 Testing audio system...');

        await this.resumeAudioContext();

        try {
            await this.playGreeting();
            setTimeout(() => this.playNumber(3), 2000);
            setTimeout(() => this.playSuccess(), 4000);

            console.log('✅ Audio test completed');
        } catch (error) {
            console.error('❌ Audio test failed:', error);
        }
    }

    // Diagnostic method to test audio file loading
    async testAudioFiles() {
        console.log('🔍 Testing all audio files...');

        const testFiles = [
            { name: 'greeting', path: this.audioFiles.greetings.hi_ready_to_play },
            { name: 'show_fingers', path: this.audioFiles.instructions.show_me_your_fingers },
            { name: 'lets_count', path: this.audioFiles.instructions.lets_start_counting },
            { name: 'number_1', path: this.audioFiles.numbers[1] },
            { name: 'number_2', path: this.audioFiles.numbers[2] }
        ];

        for (const file of testFiles) {
            try {
                console.log(`🧪 Testing ${file.name}: ${this.audioBasePath}${file.path}`);
                await this.loadAudio(file.path, false);
                console.log(`✅ ${file.name} loaded successfully`);
            } catch (error) {
                console.error(`❌ ${file.name} failed to load:`, error);
            }
        }
    }

    // Cleanup
    destroy() {
        if (this.audioContext) {
            this.audioContext.close();
        }

        // Clear caches
        this.audioCache.clear();
        this.loadingPromises.clear();

        console.log('🔊 Audio Manager destroyed');
    }
}

// Export for use in other scripts
window.AudioManager = AudioManager;