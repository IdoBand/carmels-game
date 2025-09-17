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

    # Set reasonable resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("🚀 System started! Press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        # Flip for mirror effect
        frame = cv2.flip(frame, 1)

        # Convert to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process with MediaPipe
        results = hands.process(rgb)

        finger_count = 0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Count fingers
                finger_count = count_fingers(hand_landmarks.landmark)

                # Only show numbers 1-5
                if 1 <= finger_count <= 5:
                    print(f"🔢 Detected: {finger_count}")

        # Display result
        if 1 <= finger_count <= 5:
            text = f"Number: {finger_count}"
            color = (0, 255, 0)
        else:
            text = "Show 1-5 fingers"
            color = (0, 0, 255)

        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, "Press 'q' to quit", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow('Hand Gesture Recognition', frame)

        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    print("✅ Done!")

if __name__ == "__main__":
    main()