import cv2
import numpy as np

class DisplayManager:
    def __init__(self, window_name="Hand Gesture Recognition", show_landmarks=False):
        self.window_name = window_name
        self.show_landmarks = show_landmarks
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 2
        self.thickness = 3

    def setup_window(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)

    def render_frame(self, frame, detected_number=None, hand_landmarks=None, gesture_detector=None):
        if frame is None or frame.size == 0:
            return

        try:
            # Ensure frame is safe to work with
            if not frame.flags['C_CONTIGUOUS']:
                frame = frame.copy()

            display_frame = frame.copy()

            if self.show_landmarks and hand_landmarks and gesture_detector:
                display_frame = gesture_detector.draw_landmarks(display_frame, hand_landmarks)

            display_frame = self._add_text_overlay(display_frame, detected_number)

            cv2.imshow(self.window_name, display_frame)

        except Exception as e:
            print(f"Display error: {e}")
            # Try to show a basic frame without overlays
            try:
                cv2.imshow(self.window_name, frame)
            except:
                pass

    def _add_text_overlay(self, frame, detected_number):
        height, width = frame.shape[:2]

        if detected_number is not None:
            text = f"Number: {detected_number}"
            color = (0, 255, 0)
        else:
            text = "No gesture detected"
            color = (0, 0, 255)

        text_size = cv2.getTextSize(text, self.font, self.font_scale, self.thickness)[0]
        text_x = (width - text_size[0]) // 2
        text_y = 80

        cv2.rectangle(frame,
                     (text_x - 20, text_y - text_size[1] - 20),
                     (text_x + text_size[0] + 20, text_y + 20),
                     (0, 0, 0), -1)

        cv2.putText(frame, text, (text_x, text_y),
                   self.font, self.font_scale, color, self.thickness)

        instructions = [
            "Press 'q' to quit",
            "Press 'l' to toggle landmarks",
            "Show numbers 1-5 with your hand"
        ]

        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, height - 80 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        return frame

    def check_quit_key(self):
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return True
        elif key == ord('l'):
            self.show_landmarks = not self.show_landmarks
            print(f"Landmarks display: {'ON' if self.show_landmarks else 'OFF'}")
        return False

    def cleanup(self):
        cv2.destroyAllWindows()