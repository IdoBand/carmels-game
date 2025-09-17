# Hand Gesture Recognition - PRD

## Project Overview
A Python-based real-time hand gesture recognition system that detects numeric finger gestures (1-5) using computer vision.

## Technical Stack
- **Python 3.8+**
- **OpenCV** - Video capture and display
- **MediaPipe** - Hand detection and landmark tracking

## Core Functionality

### Phase 1: Number Detection (Current Scope)
**Objective**: Detect and recognize hand gestures representing numbers 1-5

**Requirements**:
- Real-time video camera input processing
- Live video display with overlay information
- Hand gesture recognition for numbers 1-5
- Event-driven handler system for detected gestures

### Target Gestures
| Number | Gesture Description |
|--------|-------------------|
| 1 | Index finger extended |
| 2 | Index and middle fingers (peace sign) |
| 3 | Index, middle, and ring fingers |
| 4 | Four fingers (no thumb) |
| 5 | All five fingers extended |

## System Architecture

### Core Components
1. **VideoCapture Handler**
   - Initialize camera input
   - Capture frames in real-time
   - Handle camera errors/disconnection

2. **GestureDetector**
   - Process video frames using MediaPipe
   - Analyze hand landmarks
   - Classify finger positions
   - Return detected number (1-5 or None)

3. **EventHandler System**
   - Register callback functions for specific gestures
   - Invoke handlers when gestures are detected
   - Handle gesture state changes (enter/exit)

4. **DisplayManager**
   - Render live video feed
   - Overlay detected number on screen
   - Show hand landmarks (optional/debug mode)

## Functional Requirements

### FR1: Real-time Video Processing
- **Input**: Default camera (webcam)
- **Output**: Live video window with gesture overlays
- **Performance**: Minimum 15 FPS processing
- **Display**: Mirror mode for natural interaction

### FR2: Gesture Recognition
- **Accuracy**: 90%+ recognition rate for clear gestures
- **Detection Range**: Hand within 0.5-2 meters from camera
- **Lighting**: Functional in normal indoor lighting
- **Hand Orientation**: Support both left and right hands

### FR3: Event Handler System
```python
# Example handler registration
def on_number_detected(number):
    print(f"Detected number: {number}")

detector.register_handler(on_number_detected)
```

### FR4: Visual Feedback
- Display detected number prominently on screen
- Show "No gesture detected" when appropriate
- Optional: Display finger status for debugging

## Technical Specifications

### Input Requirements
- Camera resolution: 640x480 minimum
- Color format: BGR (OpenCV standard)
- Frame rate: 30 FPS capture target

### Processing Pipeline
1. Frame capture from camera
2. Convert BGR to RGB for MediaPipe
3. Hand detection and landmark extraction
4. Finger position analysis
5. Gesture classification
6. Handler invocation (if gesture detected)
7. Display update with results

### Error Handling
- Camera initialization failure
- No hand detected in frame
- Ambiguous gesture (partial recognition)
- Multiple hands detected (use primary hand)

## Project Structure
```
hand_gesture_project/
├── main.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── video_capture.py    # Camera handling
│   ├── gesture_detector.py # MediaPipe processing
│   ├── event_handler.py    # Handler system
│   └── display_manager.py  # Video display
├── requirements.txt
└── README.md
```

## Success Criteria
- [ ] Real-time video display with <100ms latency
- [ ] Reliable number detection (1-5) with 90%+ accuracy
- [ ] Smooth handler invocation without frame drops
- [ ] Clean, extensible codebase for future movement detection

## Future Considerations (Phase 2)
- Hand movement tracking (direction, speed)
- Dynamic gestures (swipes, circles)
- Multi-hand support
- Gesture customization/training

## Dependencies
```txt
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
```

## Acceptance Criteria
1. Application starts and displays live camera feed
2. Shows numbers 1-5 when corresponding hand gestures are made
3. Handler functions are called correctly when gestures are detected
4. System runs smoothly without crashes for extended periods
5. Code is modular and easily extensible