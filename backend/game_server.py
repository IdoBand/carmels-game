#!/usr/bin/env python3

import threading
import time
import base64
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import numpy as np
import os

class GameServer:
    def __init__(self, port=5000):
        # Set up Flask with proper static file handling
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
        self.app = Flask(__name__,
                         static_folder=frontend_dir,
                         static_url_path='')
        self.app.config['SECRET_KEY'] = 'toddler_counting_game_secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.port = port

        # Gesture detection components
        self.cap = None
        self.mp_hands = mp.solutions.hands
        self.hands = None
        self.mp_draw = mp.solutions.drawing_utils
        self.camera_thread = None
        self.is_running = False
        self.current_camera_index = 0

        # Game state
        self.last_detected_number = None
        self.detection_confidence = 0.0

        # Game flow state
        self.game_phase = 'technical_setup'  # technical_setup, user_setup, counting_game, completed
        self.current_number = 1
        self.numbers_completed = []
        self.waiting_for_gesture = False
        self.gesture_timeout_timer = None
        self.hand_detected = False
        self.game_start_time = None

        self.setup_routes()
        self.setup_socketio_events()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return self.app.send_static_file('index.html')

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self.generate_video_frames(),
                          mimetype='multipart/x-mixed-replace; boundary=frame')

    def setup_socketio_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            print(f"🔌 Client connected")
            emit('server_status', {'status': 'connected', 'message': 'Welcome to Toddler Counting Game!'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"🔌 Client disconnected")

        @self.socketio.on('start_camera')
        def handle_start_camera(data):
            camera_index = data.get('camera_index', 0)
            print(f"📹 Starting camera {camera_index}")

            if self.start_camera(camera_index):
                emit('camera_status', {'status': 'started', 'camera_index': camera_index})
                self.start_gesture_detection()

                # Automatically start user setup phase after camera starts (give more time for audio setup)
                threading.Timer(4.0, self.start_user_setup_phase).start()
            else:
                emit('camera_status', {'status': 'error', 'message': f'Cannot open camera {camera_index}'})

        @self.socketio.on('stop_camera')
        def handle_stop_camera(data=None):
            print("📹 Stopping camera")
            self.stop_camera()
            emit('camera_status', {'status': 'stopped'})

        @self.socketio.on('request_camera_test')
        def handle_camera_test(data=None):
            print("🔍 Testing available cameras")
            available_cameras = self.find_available_cameras()
            emit('camera_list', {'cameras': available_cameras})

        # Game Flow Events
        @self.socketio.on('start_user_setup')
        def handle_start_user_setup(data=None):
            print("🎮 Starting user setup phase")
            self.start_user_setup_phase()

        @self.socketio.on('hand_detected')
        def handle_hand_detected(data=None):
            print("👋 Hand detected, transitioning to counting game")
            self.hand_detected = True
            self.start_counting_game()

        @self.socketio.on('audio_finished')
        def handle_audio_finished(data):
            audio_file = data.get('file', '')
            print(f"🔊 Audio finished: {audio_file}")
            self.handle_audio_completed(audio_file)

        @self.socketio.on('restart_game')
        def handle_restart_game(data=None):
            print("🔄 Restarting game")
            self.restart_game()

    def find_available_cameras(self):
        """Find available camera indices"""
        available_cameras = []
        for i in range(5):  # Test cameras 0-4
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    # Try to set Full HD and get actual resolution
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                    # If we didn't get Full HD, try 720p
                    if width < 1920 or height < 1080:
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                    available_cameras.append({
                        'index': i,
                        'resolution': f"{width}x{height}",
                        'name': f"Camera {i}"
                    })
                cap.release()
        return available_cameras

    def start_camera(self, camera_index):
        """Initialize camera capture with Full HD resolution (from POC)"""
        if self.cap is not None:
            self.stop_camera()

        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            return False

        # Try to set Full HD resolution first (exactly like POC)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # Check what resolution we actually got
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"📺 Camera resolution: {actual_width}x{actual_height}")

        # If we didn't get Full HD, try 720p
        if actual_width < 1920 or actual_height < 1080:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"📺 Fallback to: {actual_width}x{actual_height}")

        # Last resort: VGA
        if actual_width < 1280 or actual_height < 720:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"📺 Using VGA: {actual_width}x{actual_height}")

        # Initialize MediaPipe hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.current_camera_index = camera_index
        return True

    def stop_camera(self):
        """Stop camera capture and cleanup"""
        self.is_running = False

        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join()

        if self.cap:
            self.cap.release()
            self.cap = None

        if self.hands:
            self.hands.close()
            self.hands = None

    def count_fingers(self, landmarks):
        """Simple finger counting (from POC)"""
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

    def start_gesture_detection(self):
        """Start gesture detection in a separate thread"""
        if self.camera_thread and self.camera_thread.is_alive():
            return

        self.is_running = True
        self.camera_thread = threading.Thread(target=self._gesture_detection_loop)
        self.camera_thread.daemon = True
        self.camera_thread.start()

    def _gesture_detection_loop(self):
        """Main gesture detection loop"""
        print("🤖 Starting gesture detection loop")

        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break

            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)

            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process with MediaPipe with error handling
            try:
                results = self.hands.process(rgb_frame)
            except ValueError as e:
                if "Packet timestamp mismatch" in str(e):
                    print("⚠️ MediaPipe timestamp mismatch, skipping frame")
                    time.sleep(0.1)  # Brief pause to reset timing
                    continue
                else:
                    print(f"❌ MediaPipe error: {e}")
                    break

            finger_count = 0
            confidence = 0.0

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    finger_count = self.count_fingers(hand_landmarks.landmark)
                    confidence = 0.95  # Simplified confidence for now

                    # Handle hand detection during user setup phase
                    if self.game_phase == 'user_setup' and not self.hand_detected:
                        print("👋 Hand detected during user setup, starting counting game")
                        self.hand_detected = True
                        self.start_counting_game()

                    # Only emit if it's a valid counting number (1-5 for this game)
                    if 1 <= finger_count <= 5:
                        # Only send if the number changed
                        if finger_count != self.last_detected_number:
                            print(f"🔢 Detected: {finger_count} fingers")
                            self.socketio.emit('gesture_detected', {
                                'number': finger_count,
                                'confidence': confidence,
                                'timestamp': time.time()
                            })
                            self.last_detected_number = finger_count

                            # Check for correct gesture during counting game
                            if self.game_phase == 'counting_game' and self.waiting_for_gesture:
                                self.handle_correct_gesture(finger_count)
            else:
                # No hand detected
                if self.last_detected_number is not None:
                    print("👋 No hand detected")
                    self.socketio.emit('gesture_lost', {
                        'timestamp': time.time()
                    })
                    self.last_detected_number = None

            # Small delay to prevent overwhelming the connection
            time.sleep(0.05)  # ~20 FPS

        print("🤖 Gesture detection loop ended")

    def generate_video_frames(self):
        """Generate video frames for streaming (from POC with hand landmarks)"""
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            # Flip frame horizontally for mirror effect (like POC)
            frame = cv2.flip(frame, 1)

            # For MediaPipe processing, we'll work with a smaller version for performance
            # But display the full resolution frame (exactly like POC)
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

            # Process with MediaPipe with error handling
            if self.hands:
                try:
                    results = self.hands.process(rgb)
                except ValueError as e:
                    if "Packet timestamp mismatch" in str(e):
                        print("⚠️ MediaPipe timestamp mismatch in video stream, skipping frame")
                        time.sleep(0.03)
                        continue
                    else:
                        print(f"❌ MediaPipe video error: {e}")
                        break

                finger_count = 0

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw individual landmark points (from POC)
                        for landmark in hand_landmarks.landmark:
                            x_pixel = int(landmark.x * width)
                            y_pixel = int(landmark.y * height)
                            cv2.circle(frame, (x_pixel, y_pixel), 5, (0, 255, 0), -1)

                        # Draw connections between landmarks (from POC)
                        for connection in self.mp_hands.HAND_CONNECTIONS:
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
                        finger_count = self.count_fingers(hand_landmarks.landmark)

                        # Only show numbers 1-10 (expanded from POC)
                        if 1 <= finger_count <= 10:
                            # Emit gesture to frontend
                            self.socketio.emit('gesture_detected', {
                                'number': finger_count,
                                'confidence': 0.95,
                                'timestamp': time.time()
                            })
                            self.last_detected_number = finger_count
                else:
                    # No hand detected
                    if self.last_detected_number is not None:
                        self.socketio.emit('gesture_lost', {'timestamp': time.time()})
                        self.last_detected_number = None


            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            time.sleep(0.03)  # ~30 FPS

    # Game Flow Management Methods
    def start_user_setup_phase(self):
        """Start user setup phase after camera is running"""
        print("🎮 Starting user setup phase")
        self.game_phase = 'user_setup'
        self.hand_detected = False

        # Emit phase change to frontend
        self.socketio.emit('game_phase_changed', {
            'phase': 'user_setup',
            'message': 'Playing greeting audio'
        })

        # Start the user setup sequence - just play the greeting first
        self.socketio.emit('play_audio', {'file': 'hi_ready_to_play'})

    def handle_audio_completed(self, audio_file):
        """Handle when audio playback is completed"""
        print(f"🔊 Audio completed: {audio_file}")

        if self.game_phase == 'user_setup':
            if 'hi_ready_to_play' in audio_file:
                # Wait 2 seconds then play next instruction
                threading.Timer(2.0, self.play_show_fingers).start()
            elif 'show_me_your_fingers' in audio_file:
                # Start monitoring for hand detection
                self.start_hand_monitoring()

        elif self.game_phase == 'counting_game':
            if any(num in audio_file for num in ['one', 'two', 'three', 'four', 'five']):
                # Number audio finished, start 15-second timer
                self.start_gesture_timeout()

    def play_show_fingers(self):
        """Play the show fingers instruction"""
        self.socketio.emit('play_audio', {'file': 'show_me_your_fingers'})

    def start_hand_monitoring(self):
        """Start monitoring for hand detection during user setup"""
        print("👋 Monitoring for hand detection...")
        # The hand detection will be handled by the existing gesture detection loop
        # When a hand is detected, it will trigger the transition

    def start_counting_game(self):
        """Start the counting game after hand is detected"""
        if self.game_phase != 'user_setup':
            return

        print("🎮 Starting counting game")
        self.game_phase = 'counting_game'
        self.current_number = 1
        self.numbers_completed = []

        # Play "let's start counting" then start with number 1
        self.socketio.emit('game_phase_changed', {
            'phase': 'counting_game',
            'current_number': self.current_number
        })

        self.socketio.emit('play_audio', {'file': 'lets_start_counting'})

        # After audio finishes, wait a bit longer then start with number 1
        threading.Timer(5.0, self.start_current_number).start()

    def start_current_number(self):
        """Start the current number challenge"""
        print(f"🔢 Starting number {self.current_number}")

        self.waiting_for_gesture = True

        # Emit number started event
        self.socketio.emit('number_started', {
            'number': self.current_number,
            'timeout': 15000  # 15 seconds
        })

        # Play the number audio immediately
        self.socketio.emit('play_audio', {'file': f'number_{self.current_number}'})

    def start_gesture_timeout(self):
        """Start 15-second timeout for gesture detection"""
        print(f"⏰ Starting 15-second timeout for number {self.current_number}")

        # Cancel any existing timer
        if self.gesture_timeout_timer:
            self.gesture_timeout_timer.cancel()

        # Start new timer
        self.gesture_timeout_timer = threading.Timer(15.0, self.handle_gesture_timeout)
        self.gesture_timeout_timer.start()

    def handle_gesture_timeout(self):
        """Handle when gesture timeout expires"""
        if not self.waiting_for_gesture:
            return  # Gesture was already detected

        print(f"⏰ Timeout for number {self.current_number}, replaying audio")

        # Replay the number audio
        self.socketio.emit('play_audio', {'file': f'number_{self.current_number}'})

        # Don't cancel waiting_for_gesture - keep waiting
        # The timeout will be restarted when audio finishes

    def handle_correct_gesture(self, detected_number):
        """Handle when correct gesture is detected"""
        if not self.waiting_for_gesture or detected_number != self.current_number:
            return

        print(f"✅ Correct gesture detected: {detected_number}")

        # Cancel timeout timer
        if self.gesture_timeout_timer:
            self.gesture_timeout_timer.cancel()
            self.gesture_timeout_timer = None

        self.waiting_for_gesture = False

        # Add to completed numbers
        self.numbers_completed.append(self.current_number)

        # Emit success event
        self.socketio.emit('number_success', {
            'number': self.current_number,
            'completed': self.numbers_completed
        })

        # Play random positive feedback
        self.socketio.emit('play_random_positive_feedback', {})

        # Move to next number after a longer delay to let positive feedback finish
        if self.current_number < 5:
            threading.Timer(4.0, self.move_to_next_number).start()
        else:
            threading.Timer(4.0, self.complete_game).start()

    def move_to_next_number(self):
        """Move to the next number in sequence"""
        self.current_number += 1
        print(f"➡️ Moving to number {self.current_number}")

        self.socketio.emit('next_number', {
            'number': self.current_number,
            'progress': len(self.numbers_completed)
        })

        # Start the new number
        self.start_current_number()

    def complete_game(self):
        """Complete the game when all numbers are done"""
        print("🎉 Game completed!")
        self.game_phase = 'completed'

        self.socketio.emit('game_completed', {
            'numbers_completed': self.numbers_completed,
            'completion_time': time.time() - self.game_start_time if self.game_start_time else 0
        })

    def restart_game(self):
        """Restart the game from the beginning"""
        print("🔄 Restarting game")

        # Cancel any timers
        if self.gesture_timeout_timer:
            self.gesture_timeout_timer.cancel()
            self.gesture_timeout_timer = None

        # Reset game state
        self.game_phase = 'technical_setup'
        self.current_number = 1
        self.numbers_completed = []
        self.waiting_for_gesture = False
        self.hand_detected = False
        self.game_start_time = None

        # Emit restart event
        self.socketio.emit('game_restarted', {})

    def run(self, debug=False):
        """Start the Flask-SocketIO server"""
        print(f"🚀 Starting Toddler Counting Game server on port {self.port}")
        print(f"🌐 Access the game at: http://localhost:{self.port}")

        try:
            self.socketio.run(
                self.app,
                host='0.0.0.0',
                port=self.port,
                debug=debug
            )
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
        finally:
            self.stop_camera()

if __name__ == '__main__':
    server = GameServer(port=5000)
    server.run(debug=True)