// Audio Manager for Toddler Counting Game

class AudioManager {
    constructor() {
        // Audio context and settings
        this.audioContext = null;
        this.masterVolume = 0.7;
        this.speechVolume = 0.8;
        this.effectsVolume = 0.6;

        // Audio file paths
        this.audioBasePath = 'assets/audio/';
        this.audioFiles = {
            numbers: {
                1: 'numbers/one.mp3',
                2: 'numbers/two.mp3',
                3: 'numbers/three.mp3',
                4: 'numbers/four.mp3',
                5: 'numbers/five.mp3',
                6: 'numbers/six.mp3',
                7: 'numbers/seven.mp3',
                8: 'numbers/eight.mp3',
                9: 'numbers/nine.mp3',
                10: 'numbers/ten.mp3'
            },
            feedback: {
                success: 'feedback/great-job.mp3',
                try_again: 'feedback/try-again.mp3',
                victory: 'feedback/amazing.mp3',
                greeting: 'feedback/hi-there.mp3',
                start: 'feedback/lets-count.mp3'
            },
            instructions: {
                show_fingers: 'instructions/show-me-fingers.mp3',
                start_game: 'instructions/show-one-finger.mp3'
            }
        };

        // Speech synthesis settings
        this.speechSettings = {
            rate: 0.7,        // Slower for toddlers
            pitch: 1.2,       // Higher pitch, friendlier
            volume: 0.8,
            voice: null       // Will be set to best child-friendly voice
        };

        // Audio cache
        this.audioCache = new Map();
        this.loadingPromises = new Map();

        // Speech synthesis
        this.speechSynth = window.speechSynthesis;
        this.currentUtterance = null;

        // State
        this.isInitialized = false;
        this.isMuted = false;
        this.preferSynthesis = true; // Use speech synthesis as fallback

        this.initialize();
    }

    async initialize() {
        console.log('🔊 Initializing Audio Manager...');

        try {
            // Initialize Web Audio API context
            await this.initializeAudioContext();

            // Setup speech synthesis
            this.setupSpeechSynthesis();

            // Try to preload critical audio files
            await this.preloadCriticalAudio();

            this.isInitialized = true;
            console.log('✅ Audio Manager initialized successfully');

        } catch (error) {
            console.warn('⚠️ Audio initialization error:', error);
            this.isInitialized = true; // Continue with speech synthesis only
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

    setupSpeechSynthesis() {
        if (!this.speechSynth) {
            console.warn('⚠️ Speech synthesis not available');
            return;
        }

        // Wait for voices to load
        const setVoice = () => {
            const voices = this.speechSynth.getVoices();

            // Prefer child-friendly voices
            const preferredVoices = [
                'Google UK English Female',
                'Microsoft Zira - English (United States)',
                'Alex',
                'Samantha',
                'Karen'
            ];

            let selectedVoice = null;

            // Try to find a preferred voice
            for (const voiceName of preferredVoices) {
                selectedVoice = voices.find(voice => voice.name.includes(voiceName));
                if (selectedVoice) break;
            }

            // Fallback to first English voice
            if (!selectedVoice) {
                selectedVoice = voices.find(voice => voice.lang.startsWith('en')) || voices[0];
            }

            this.speechSettings.voice = selectedVoice;
            console.log('🗣️ Selected voice:', selectedVoice?.name || 'Default');
        };

        // Set voice immediately if available, or wait for voices to load
        if (this.speechSynth.getVoices().length > 0) {
            setVoice();
        } else {
            this.speechSynth.addEventListener('voiceschanged', setVoice);
        }
    }

    async preloadCriticalAudio() {
        // Preload the most important audio files
        const criticalFiles = [
            this.audioFiles.feedback.greeting,
            this.audioFiles.feedback.success,
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

        // Check cache
        if (this.audioCache.has(fullPath)) {
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
                console.warn(`⚠️ Failed to load audio: ${fullPath}`, error);
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
            audioElement.volume = this.effectsVolume * this.masterVolume;
            audioElement.currentTime = 0;
            await audioElement.play();
            return audioElement;
        } catch (error) {
            console.warn('⚠️ Audio playback error:', error);
            throw error;
        }
    }

    // Speech Synthesis
    speak(text, options = {}) {
        if (this.isMuted || !this.speechSynth) return;

        // Stop any current speech
        this.stopSpeech();

        const utterance = new SpeechSynthesisUtterance(text);

        // Apply settings
        utterance.rate = options.rate || this.speechSettings.rate;
        utterance.pitch = options.pitch || this.speechSettings.pitch;
        utterance.volume = (options.volume || this.speechSettings.volume) * this.masterVolume;
        utterance.voice = options.voice || this.speechSettings.voice;

        // Event handlers
        utterance.onstart = () => {
            console.log(`🗣️ Speaking: "${text}"`);
        };

        utterance.onend = () => {
            this.currentUtterance = null;
        };

        utterance.onerror = (error) => {
            console.warn('⚠️ Speech synthesis error:', error);
            this.currentUtterance = null;
        };

        this.currentUtterance = utterance;
        this.speechSynth.speak(utterance);

        return utterance;
    }

    stopSpeech() {
        if (this.currentUtterance) {
            this.speechSynth.cancel();
            this.currentUtterance = null;
        }
    }

    // High-Level Audio Methods
    async playNumber(number) {
        console.log(`🔊 Playing number: ${number}`);

        try {
            const audioFile = this.audioFiles.numbers[number];
            if (audioFile) {
                await this.loadAudio(audioFile, true);
            } else {
                throw new Error('Audio file not configured');
            }
        } catch (error) {
            // Fallback to speech synthesis
            const text = this.getNumberText(number);
            this.speak(text);
        }
    }

    async playInstruction(instruction) {
        console.log(`🔊 Playing instruction: ${instruction}`);

        const instructionTexts = {
            'show_fingers': 'Show me your fingers!',
            'show_one_finger': 'Show me one finger to start!',
            'show_number': (num) => `Show me ${this.getNumberText(num)} finger${num > 1 ? 's' : ''}!`,
            'great_job': 'Great job!',
            'try_again': 'Try again!',
            'amazing': 'Amazing! You did it!',
            'hi_there': 'Hi there! Ready to count?',
            'lets_count': 'Let\'s count together!'
        };

        try {
            const audioFile = this.audioFiles.instructions[instruction] || this.audioFiles.feedback[instruction];
            if (audioFile) {
                await this.loadAudio(audioFile, true);
            } else {
                throw new Error('Audio file not found');
            }
        } catch (error) {
            // Fallback to speech synthesis
            let text = instructionTexts[instruction] || instruction;
            if (typeof text === 'function') {
                text = text(1); // Default to 1 for dynamic instructions
            }
            this.speak(text);
        }
    }

    async playNumberInstruction(number) {
        console.log(`🔊 Playing number instruction: ${number}`);

        const text = `Show me ${this.getNumberText(number)} finger${number > 1 ? 's' : ''}!`;

        try {
            // Try to find a specific instruction audio file
            const instructionFile = `instructions/show-${number}.mp3`;
            await this.loadAudio(instructionFile, true);
        } catch (error) {
            // Fallback to speech synthesis
            this.speak(text);
        }
    }

    async playSuccess() {
        console.log('🔊 Playing success sound');

        try {
            await this.loadAudio(this.audioFiles.feedback.success, true);
        } catch (error) {
            this.speak('Great job!', { pitch: 1.4, rate: 0.8 });
        }
    }

    async playTryAgain() {
        console.log('🔊 Playing try again sound');

        try {
            await this.loadAudio(this.audioFiles.feedback.try_again, true);
        } catch (error) {
            this.speak('Try again!', { pitch: 1.3 });
        }
    }

    async playVictory() {
        console.log('🔊 Playing victory sound');

        try {
            await this.loadAudio(this.audioFiles.feedback.victory, true);
        } catch (error) {
            this.speak('Amazing! You counted to ten!', {
                pitch: 1.5,
                rate: 0.6,
                volume: 1.0
            });
        }
    }

    async playGreeting() {
        console.log('🔊 Playing greeting');

        try {
            await this.loadAudio(this.audioFiles.feedback.greeting, true);
        } catch (error) {
            this.speak('Hi there! Ready to count with me?', {
                pitch: 1.3,
                rate: 0.7
            });
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

    setSpeechVolume(volume) {
        this.speechVolume = Math.max(0, Math.min(1, volume));
        console.log(`🗣️ Speech volume set to: ${this.speechVolume}`);
    }

    setEffectsVolume(volume) {
        this.effectsVolume = Math.max(0, Math.min(1, volume));
        console.log(`🎵 Effects volume set to: ${this.effectsVolume}`);
    }

    toggleMute() {
        this.isMuted = !this.isMuted;
        if (this.isMuted) {
            this.stopSpeech();
        }
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

    // Cleanup
    destroy() {
        this.stopSpeech();

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