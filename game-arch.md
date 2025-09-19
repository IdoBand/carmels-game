# Toddler Counting Game - Technical Architecture

## 🎯 Project Vision
Create an interactive counting game for toddlers (ages 2-5) that uses hand gesture recognition to teach numbers 1-10. The game features a friendly avatar, voice guidance, and celebrates successful counting gestures.

## 🏗️ Technical Architecture

### **Hybrid Web + Python System**

```
┌─────────────────────┐    WebSocket    ┌─────────────────────┐
│   Python Backend    │ ←─────────────→ │   Web Frontend      │
│                     │                 │                     │
│ • Camera selection  │                 │ • Avatar display    │
│ • Gesture detection │                 │ • Audio playback    │
│ • Game logic        │                 │ • Visual feedback   │
│ • State management  │                 │ • Static images     │
│ • WebSocket server  │                 │ • Toddler-friendly  │
└─────────────────────┘                 └─────────────────────┘
```

### **Component Breakdown**

#### **Backend (Python)**
- **Existing Components**: VideoCapture, GestureDetector, EventHandler
- **New Components**:
  - WebSocket server (Flask-SocketIO or similar)
  - Game state manager
  - Audio file coordinator
  - Real-time communication handler

#### **Frontend (Web Browser)**
- **Technology**: HTML5, CSS3, JavaScript
- **Features**:
  - Responsive design for toddlers
  - Static avatar image display
  - Web Audio API for voiceovers
  - Visual celebrations and feedback

## 🎮 Game Flow Design

### **Phase 1: Setup & Greeting**
1. **Camera Selection** (current system)
2. **Auto-launch browser** with game URL
3. **Avatar greeting**: "Hi! I'm [Character Name]!"
4. **Instruction**: "Show me a thumbs up to start playing!"
5. **Wait for thumbs up gesture**

### **Phase 2: Counting Game Loop**
```
For each number from 1 to 10:
├─ Avatar announces: "Show me [NUMBER] fingers!"
├─ Visual cue: Display number as dots/objects
├─ Play voiceover file: "number_3.mp3"
├─ Wait for correct hand gesture
├─ On success:
│  ├─ Celebration animation
│  ├─ "Great job!" voiceover
│  └─ Move to next number
├─ On incorrect gesture:
│  ├─ Gentle feedback: "Try again!"
│  └─ Repeat instruction
└─ Continue until number 10
```

### **Phase 3: Completion & Celebration**
1. **Victory sequence**: "You counted to 10! Amazing!"
2. **Celebration animation** with confetti/stars
3. **Option to play again**

## 🎨 Visual Design Principles

### **Toddler-Friendly Interface**
- **Color Palette**: Bright, cheerful colors (pastels + primary)
- **Typography**: Large, rounded fonts (Comic Sans style)
- **Layout**: Simple, uncluttered, focus on avatar
- **Feedback**: Immediate visual responses
- **Accessibility**: High contrast, large touch targets

### **Avatar Character**
- **Style**: Static image (home2.png)
- **Display**: Circular, friendly presentation
- **Consistency**: Same image throughout experience
- **Function**: Visual anchor and speech bubble host

## 🔊 Audio System

### **Voice Requirements**
- **Tone**: Warm, encouraging, child-friendly
- **Pace**: Slower speech for comprehension
- **Files**: Individual MP3s for each instruction
- **Structure**:
  ```
  audio/
  ├─ greeting.mp3
  ├─ instructions_start.mp3
  ├─ numbers/
  │  ├─ show_1.mp3
  │  ├─ show_2.mp3
  │  └─ ...show_10.mp3
  ├─ feedback/
  │  ├─ great_job.mp3
  │  ├─ try_again.mp3
  │  └─ amazing.mp3
  └─ victory.mp3
  ```

## 📂 Project Structure

```
carmels-game/
├─ backend/
│  ├─ src/                    # Current gesture recognition
│  ├─ game_server.py          # WebSocket server
│  ├─ game_logic.py           # Game state management
│  └─ main.py                 # Application launcher
├─ frontend/
│  ├─ index.html              # Main game interface
│  ├─ css/
│  │  └─ toddler-styles.css   # Colorful, child-friendly CSS
│  ├─ js/
│  │  ├─ game-client.js       # WebSocket client
│  │  └─ audio-manager.js     # Audio playback control
│  └─ assets/
│     ├─ images/              # Avatar and number images (1.png-5.png, home2.png)
│     └─ audio/               # Voiceover files
├─ requirements.txt           # Python dependencies
├─ README.md                  # Updated usage instructions
└─ game-arch.md              # This document
```

## 🔄 Communication Protocol

### **WebSocket Events**
```javascript
// Python → Web
{
  "event": "gesture_detected",
  "data": {"number": 3, "confidence": 0.95}
}

{
  "event": "game_state",
  "data": {"current_number": 3, "phase": "waiting_for_gesture"}
}

// Web → Python
{
  "event": "start_game",
  "data": {}
}

{
  "event": "audio_finished",
  "data": {"file": "show_3.mp3"}
}
```

## 🚀 Implementation Phases

### **Phase 1: Foundation** ✅ COMPLETED
- [x] Improve camera resolution to Full HD
- [x] Create basic web server with WebSocket
- [x] Build simple web interface
- [x] Establish Python ↔ Web communication

**✅ Completed Components:**
- Restructured project with `backend/` and `frontend/` folders
- Created `backend/game_server.py` - Flask-SocketIO WebSocket server
- Built responsive HTML interface with toddler-friendly CSS
- Established real-time communication between Python and web frontend
- Added camera detection and selection system
- Implemented Full HD camera resolution support

### **Phase 2: Real-time Video & Gesture Detection** ✅ COMPLETED
- [x] Real-time video streaming with hand landmark visualization
- [x] Full HD resolution support with proper fallback
- [x] MediaPipe hand tracking integration
- [x] Large video display optimized for toddler feedback
- [x] Basic gesture detection and display

**✅ Completed Components:**
- **Real-time Video Streaming**: Added `/video_feed` endpoint streaming live camera with hand landmarks
- **Hand Landmark Visualization**: MediaPipe integration with green dots and white lines overlay
- **Full HD Resolution**: Proper camera resolution detection and fallback (1920x1080 → 1280x720 → 640x480)
- **Large Video Display**: 90% viewport sizing with proper centering for maximum toddler visibility
- **Gesture Detection**: Real-time finger counting (1-10) with visual feedback
- **Clean UI**: Setup interface hidden when video active, video becomes primary interface
- **Number Display Overlay**: Bottom-right overlay showing target number with PNG images
- **Mirror Effect**: Horizontally flipped video for natural interaction

### **Phase 3: Game Logic & Flow** ✅ COMPLETED
- [x] Implement counting game progression (1-5 sequence)
- [x] Add game state management (setup, user setup, counting game, completion)
- [x] Create encouragement and feedback system
- [x] Add restart/replay functionality
- [x] Implement 15-second timeout with audio replay
- [x] Add proper audio completion callbacks
- [x] Remove all AI voice fallbacks

**✅ Completed Components:**
- **Game State Management**: Complete phase tracking (technical_setup → user_setup → counting_game → completed)
- **Audio System Integration**: MP3-only audio with proper completion callbacks
- **Counting Sequence**: Numbers 1-5 with timeout and replay logic
- **Positive Feedback**: Random selection from 3 positive feedback audio files
- **Clean Video Stream**: Removed all text overlays, hand landmarks only
- **Timing System**: 2-second delays between audio for clarity

### **Phase 4: Audio & Polish** ✅ COMPLETED
- [x] Record child-friendly voiceovers for numbers and encouragement
- [x] Add comprehensive audio library with proper file structure
- [x] Implement MP3-only audio system (removed AI voice entirely)
- [x] Create proper audio file organization
- [x] Add audio completion tracking

**✅ Completed Components:**
- **Audio File Structure**: Organized into greetings/, instructions/, numbers/, positive_feedback/, encouragement/
- **No AI Voice**: Completely removed speech synthesis fallbacks
- **Audio Manager**: Full MP3 playback system with Web Audio API
- **Audio Callbacks**: Proper event handling for audio completion
- **Volume Control**: Master volume and effects volume controls

### **Phase 5: Advanced Features** ⏳ FUTURE
- [ ] Advanced gesture recognition (thumbs up, peace sign, etc.)
- [ ] Multiple difficulty levels and game modes
- [ ] Progress tracking and statistics
- [ ] Parent dashboard and settings
- [ ] Localization support
- [ ] Extend to numbers 6-10

## 🎯 Current Status

**✅ FULLY WORKING:**
- Complete game flow from camera setup to counting game
- Real-time video feed with clean hand tracking visualization (no text overlays)
- Accurate finger counting detection (1-5) with MediaPipe integration
- Full HD camera resolution support with proper fallbacks
- Large, toddler-focused video display (90% viewport)
- Complete audio system with MP3 files (NO AI voice)
- Game state management with proper phase transitions
- Audio completion callbacks and timing systems
- Random positive feedback selection
- 15-second timeout with audio replay functionality

**🎮 READY FOR PRODUCTION:**
- Complete toddler counting game (numbers 1-5)
- Full game flow: Technical Setup → User Setup → Counting Game → Completion
- All audio files integrated and working
- Clean, professional video stream with hand landmarks only
- Robust error handling and MediaPipe timestamp protection

## 🎯 Future Success Criteria

- [ ] Toddlers can successfully complete counting 1-10 game sequence
- [ ] Interface is engaging and holds attention for extended periods
- [ ] Audio guidance is clear and encouraging
- [ ] System works reliably with various webcam types
- [ ] Parents find it educational and valuable
- [ ] Game progression keeps toddlers motivated

## 🔧 Technical Requirements

### **Performance**
- **Gesture Detection**: <100ms latency
- **Audio Playback**: Seamless transitions
- **Visual Feedback**: 60fps animations
- **Camera Resolution**: Full HD (1920x1080) support

### **Compatibility**
- **Operating Systems**: Windows 10+, macOS, Linux
- **Browsers**: Chrome, Firefox, Safari, Edge
- **Hardware**: USB webcams, built-in cameras
- **Python**: 3.8+ with OpenCV, MediaPipe

### **Extensibility**
- **Modular design** for easy feature addition
- **Configuration files** for audio and visual assets
- **Plugin architecture** for new games/activities
- **Localization support** for multiple languages