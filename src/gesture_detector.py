import cv2
import mediapipe as mp
import numpy as np
import logging

class GestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.last_detected_number = None

    def _count_extended_fingers(self, landmarks):
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]

        extended_fingers = []

        # Thumb (different logic due to different orientation)
        if landmarks[finger_tips[0]].x > landmarks[finger_pips[0]].x:
            extended_fingers.append(1)
        else:
            extended_fingers.append(0)

        # Other fingers
        for i in range(1, 5):
            if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
                extended_fingers.append(1)
            else:
                extended_fingers.append(0)

        return extended_fingers

    def _classify_gesture(self, extended_fingers):
        total_extended = sum(extended_fingers)

        if total_extended == 0:
            return None
        elif total_extended == 1:
            # Check if it's index finger only
            if extended_fingers[1] == 1 and sum(extended_fingers[0:1] + extended_fingers[2:]) == 0:
                return 1
        elif total_extended == 2:
            # Peace sign - index and middle finger
            if extended_fingers[1] == 1 and extended_fingers[2] == 1 and sum(extended_fingers[0:1] + extended_fingers[3:]) == 0:
                return 2
        elif total_extended == 3:
            # Three fingers - index, middle, ring
            if extended_fingers[1] == 1 and extended_fingers[2] == 1 and extended_fingers[3] == 1 and extended_fingers[0] == 0 and extended_fingers[4] == 0:
                return 3
        elif total_extended == 4:
            # Four fingers (no thumb)
            if sum(extended_fingers[1:]) == 4 and extended_fingers[0] == 0:
                return 4
        elif total_extended == 5:
            # All fingers extended
            if all(extended_fingers):
                return 5

        return None

    def detect_gesture(self, frame):
        # Ensure frame is valid and properly formatted
        if frame is None or frame.size == 0:
            return None, None

        # MediaPipe works better with smaller resolutions - resize if too large
        height, width = frame.shape[:2]
        if width > 1280 or height > 720:
            # Resize to 720p for MediaPipe processing
            scale_factor = min(1280/width, 720/height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            frame = cv2.resize(frame, (new_width, new_height))

        # Ensure frame is contiguous in memory
        if not frame.flags['C_CONTIGUOUS']:
            frame = np.ascontiguousarray(frame)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        detected_number = None
        hand_landmarks = None

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                hand_landmarks = landmarks
                extended_fingers = self._count_extended_fingers(landmarks.landmark)
                detected_number = self._classify_gesture(extended_fingers)
                break

        # Update last detected number if we have a valid detection
        if detected_number is not None:
            self.last_detected_number = detected_number

        return detected_number, hand_landmarks

    def draw_landmarks(self, frame, hand_landmarks):
        if hand_landmarks:
            self.mp_draw.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return frame

    def cleanup(self):
        if self.hands:
            self.hands.close()