# Hand Gesture Recognition System

A Python-based real-time hand gesture recognition system that detects numeric finger gestures (1-5) using computer vision.

## Features

- Real-time video processing with live camera feed
- Hand gesture recognition for numbers 1-5
- Event-driven handler system for detected gestures
- Visual feedback with overlay information
- Configurable landmark display for debugging

## Installation

1. Clone or download this project
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

1. **Enter camera index**: Type your camera number (usually 0 or 1) and press Enter
2. **Start recognition**: The video window will open showing your camera feed
3. **Show gestures**: Hold up 1-5 fingers to detect numbers
4. **Quit**: Press 'q' to exit

### Controls

- **Show 1-5 fingers**: The system will detect and display the number
- **'q'**: Quit the application

### Supported Gestures

| Number | Gesture Description |
|--------|-------------------|
| 1 | Index finger extended |
| 2 | Index and middle fingers (peace sign) |
| 3 | Index, middle, and ring fingers |
| 4 | Four fingers (no thumb) |
| 5 | All five fingers extended |

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
├── README.md
└── CLAUDE.md              # Project Requirements Document
```

## Technical Details

- **Camera Resolution**: 640x480 minimum
- **Target FPS**: 30 FPS capture, 15+ FPS processing
- **Detection Range**: 0.5-2 meters from camera
- **Hand Support**: Both left and right hands
- **Accuracy Target**: 90%+ recognition rate

## Dependencies

- OpenCV (opencv-python>=4.8.0)
- MediaPipe (mediapipe>=0.10.0)
- NumPy (numpy>=1.24.0)

## Customization

You can register custom event handlers for detected gestures:

```python
def my_custom_handler(number):
    print(f"Custom action for number: {number}")

# In your code
event_handler.register_handler(my_custom_handler)
```

## Troubleshooting

- **Camera not detected**: Ensure your camera is connected and not used by other applications
- **Poor recognition**: Ensure good lighting and clear hand positioning
- **Performance issues**: Check system resources and camera FPS settings