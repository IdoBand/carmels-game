import cv2
import logging

class VideoCapture:
    def __init__(self, camera_index=None, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.is_initialized = False

    def _find_working_camera(self):
        working_cameras = []
        print("🔍 Searching for available cameras...")

        # Try default camera indices first
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"✅ Found working camera at index {i}")
                    working_cameras.append(i)
                cap.release()

        # If no cameras found, try DirectShow backend (Windows specific)
        if not working_cameras:
            print("🔍 Trying DirectShow backend...")
            for i in range(5):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        print(f"✅ Found working camera at index {i} (DirectShow)")
                        working_cameras.append(i)
                    cap.release()

        return working_cameras[0] if working_cameras else None

    def initialize(self):
        # If no camera index specified, find one automatically
        if self.camera_index is None:
            self.camera_index = self._find_working_camera()
            if self.camera_index is None:
                print("❌ No working cameras found!")
                return False

        # Try multiple backends
        backends = [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_V4L2]

        for backend in backends:
            try:
                print(f"🔧 Trying to open camera {self.camera_index} with backend...")
                self.cap = cv2.VideoCapture(self.camera_index, backend)

                if not self.cap.isOpened():
                    continue

                # Test if we can actually read frames
                ret, test_frame = self.cap.read()
                if not ret:
                    self.cap.release()
                    continue

                # Configure camera properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.cap.set(cv2.CAP_PROP_FPS, 30)

                # Get actual resolution
                actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                self.is_initialized = True
                print(f"✅ Camera {self.camera_index} initialized at {actual_width}x{actual_height}")
                return True

            except Exception as e:
                logging.error(f"Failed to initialize camera with backend: {e}")
                if self.cap:
                    self.cap.release()
                continue

        logging.error(f"Failed to initialize camera {self.camera_index} with any backend")
        return False

    def read_frame(self):
        if not self.is_initialized or self.cap is None:
            return False, None

        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                logging.warning("Failed to read frame from camera")
                return False, None

            # Validate frame properties
            if frame.size == 0 or len(frame.shape) != 3:
                logging.warning("Invalid frame dimensions")
                return False, None

            # Ensure frame is contiguous and properly formatted
            if not frame.flags['C_CONTIGUOUS']:
                frame = frame.copy()

            # Mirror the frame
            frame = cv2.flip(frame, 1)

            return True, frame

        except Exception as e:
            logging.error(f"Error reading frame: {e}")
            return False, None

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.is_initialized = False
            logging.info("Camera released")

    def is_connected(self):
        return self.is_initialized and self.cap is not None and self.cap.isOpened()