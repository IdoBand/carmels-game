#!/usr/bin/env python3

import cv2
import mediapipe as mp
import numpy as np

def count_fingers(landmarks):
    """Simple finger counting"""
    finger_tips = [4, 8, 12, 16, 20]
    finger_pips = [3, 6, 10, 14, 18]

    fingers = []

    # Thumb
    if landmarks[4].x > landmarks[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for i in range(1, 5):
        if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

def main():
    print("🎥 Basic Hand Gesture Recognition")
    print("=" * 40)

    # Ask user for camera index
    try:
        camera_index = int(input("Enter camera index (0, 1, 2, etc.): "))
    except ValueError:
        camera_index = 0
        print("Using default camera 0")

    # Initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils

    # Initialize camera
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"❌ Cannot open camera {camera_index}")
        return

    # Try to set Full HD resolution first
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Check what resolution we actually got
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"📺 Camera resolution: {actual_width}x{actual_height}")

    # If we didn't get Full HD, try 720p
    if actual_width < 1920 or actual_height < 1080:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"📺 Fallback to: {actual_width}x{actual_height}")

    # Last resort: VGA
    if actual_width < 1280 or actual_height < 720:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"📺 Using VGA: {actual_width}x{actual_height}")

    print("🚀 System started!")
    print("📋 Controls:")
    print("   - 'q': Quit")
    print("   - 'f': Toggle fullscreen")
    print("   - ESC: Exit fullscreen")

    # Create window
    window_name = 'Hand Gesture Recognition'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Track fullscreen state
    is_fullscreen = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        # Flip for mirror effect
        frame = cv2.flip(frame, 1)

        # For MediaPipe processing, we'll work with a smaller version for performance
        # But display the full resolution frame
        processing_frame = frame

        # If frame is larger than 720p, create a smaller version for MediaPipe
        height, width = frame.shape[:2]
        if width > 1280 or height > 720:
            # Calculate scale to fit within 720p while maintaining aspect ratio
            scale = min(1280/width, 720/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            processing_frame = cv2.resize(frame, (new_width, new_height))

        # Convert to RGB for MediaPipe
        rgb = cv2.cvtColor(processing_frame, cv2.COLOR_BGR2RGB)

        # Process with MediaPipe
        results = hands.process(rgb)

        finger_count = 0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # The landmarks are already normalized (0-1), so we just multiply by frame dimensions
                # No need for additional scaling since MediaPipe gives normalized coordinates

                # Draw individual landmark points
                for landmark in hand_landmarks.landmark:
                    x_pixel = int(landmark.x * width)
                    y_pixel = int(landmark.y * height)
                    cv2.circle(frame, (x_pixel, y_pixel), 5, (0, 255, 0), -1)

                # Draw connections between landmarks
                for connection in mp_hands.HAND_CONNECTIONS:
                    start_idx = connection[0]
                    end_idx = connection[1]

                    start_landmark = hand_landmarks.landmark[start_idx]
                    end_landmark = hand_landmarks.landmark[end_idx]

                    start_x = int(start_landmark.x * width)
                    start_y = int(start_landmark.y * height)
                    end_x = int(end_landmark.x * width)
                    end_y = int(end_landmark.y * height)

                    cv2.line(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 2)

                # Count fingers (use landmarks from processing frame)
                finger_count = count_fingers(hand_landmarks.landmark)

                # Only show numbers 1-5
                if 1 <= finger_count <= 5:
                    print(f"🔢 Detected: {finger_count}")

        # Get frame dimensions for scaling text
        height, width = frame.shape[:2]

        # Scale text size based on window size (bigger for fullscreen)
        scale = max(width / 640, height / 480)
        font_scale = scale * 1.5 if is_fullscreen else 1
        thickness = int(scale * 3) if is_fullscreen else 2

        # Display result with scaled text
        if 1 <= finger_count <= 5:
            text = f"Number: {finger_count}"
            color = (0, 255, 0)
        else:
            text = "Show 1-5 fingers"
            color = (0, 0, 255)

        # Position text relative to frame size
        text_x = int(width * 0.1)
        text_y = int(height * 0.15)

        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

        # Instructions at bottom
        instructions = "F: Fullscreen | Q: Quit | ESC: Exit Fullscreen"
        inst_y = int(height * 0.9)
        cv2.putText(frame, instructions, (text_x, inst_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.5, (255, 255, 255), max(1, thickness // 2))

        cv2.imshow(window_name, frame)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('f'):
            # Toggle fullscreen
            if is_fullscreen:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                is_fullscreen = False
                print("📺 Windowed mode")
            else:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                is_fullscreen = True
                print("🖥️  Fullscreen mode")
        elif key == 27:  # ESC key
            if is_fullscreen:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                is_fullscreen = False
                print("📺 Exited fullscreen")

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    print("✅ Done!")

if __name__ == "__main__":
    main()