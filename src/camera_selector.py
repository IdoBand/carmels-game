import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import threading
import time

class CameraSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hand Gesture Recognition - Camera Selection")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.available_cameras = []
        self.selected_camera = None
        self.selected_camera_resolution = None
        self.preview_window = None
        self.preview_cap = None
        self.preview_running = False

        self.setup_ui()
        self.scan_cameras()

    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="Hand Gesture Recognition System",
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        subtitle_label = tk.Label(self.root, text="Select a camera to begin",
                                 font=("Arial", 10))
        subtitle_label.pack(pady=5)

        # Camera list frame
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=20, padx=20, fill="both", expand=True)

        tk.Label(list_frame, text="Available Cameras:", font=("Arial", 12, "bold")).pack(anchor="w")

        # Treeview for camera list
        columns = ("Index", "Status", "Resolution")
        self.camera_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=8)

        self.camera_tree.heading("#0", text="Camera")
        self.camera_tree.heading("Index", text="Index")
        self.camera_tree.heading("Status", text="Status")
        self.camera_tree.heading("Resolution", text="Resolution")

        self.camera_tree.column("#0", width=200)
        self.camera_tree.column("Index", width=60)
        self.camera_tree.column("Status", width=120)
        self.camera_tree.column("Resolution", width=120)

        self.camera_tree.pack(fill="both", expand=True, pady=10)

        # Bind selection event
        self.camera_tree.bind("<<TreeviewSelect>>", self.on_camera_select)

        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        self.refresh_btn = tk.Button(button_frame, text="🔄 Refresh Cameras",
                                    command=self.scan_cameras, width=15)
        self.refresh_btn.pack(side="left", padx=5)

        self.test_btn = tk.Button(button_frame, text="👁️ Test Camera",
                                 command=self.test_camera, width=15, state="disabled")
        self.test_btn.pack(side="left", padx=5)

        self.start_btn = tk.Button(button_frame, text="🚀 Start Recognition",
                                  command=self.start_recognition, width=15,
                                  state="disabled", bg="#4CAF50", fg="white")
        self.start_btn.pack(side="left", padx=5)

        # Status label
        self.status_label = tk.Label(self.root, text="Scanning for cameras...",
                                    font=("Arial", 10), fg="blue")
        self.status_label.pack(pady=10)

    def scan_cameras(self):
        self.status_label.config(text="Scanning for cameras...", fg="blue")
        self.refresh_btn.config(state="disabled")

        # Clear existing items
        for item in self.camera_tree.get_children():
            self.camera_tree.delete(item)

        self.available_cameras = []

        # Run camera detection in a separate thread to avoid UI freezing
        thread = threading.Thread(target=self._detect_cameras)
        thread.daemon = True
        thread.start()

    def _test_camera_resolutions(self, camera_index, backend=cv2.CAP_ANY):
        """Test camera with safe, compatible resolution"""
        # Force VGA resolution for maximum compatibility
        cap = cv2.VideoCapture(camera_index, backend)
        if not cap.isOpened():
            return None

        # Set VGA resolution - most compatible
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Test if we can actually read a frame
        ret, frame = cap.read()
        if ret and frame is not None and frame.size > 0:
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            return (actual_width, actual_height)

        cap.release()
        return None

    def _detect_cameras(self):
        working_cameras = []

        # Test camera indices 0-5 (reduced range for speed)
        for i in range(6):
            try:
                # First test if camera exists with basic check
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cap.release()

                        # Now test for best resolution
                        best_res = self._test_camera_resolutions(i)
                        if best_res:
                            width, height = best_res
                            resolution_text = f"{width}x{height} (Compatible)"

                            working_cameras.append({
                                'index': i,
                                'name': f"Camera {i}",
                                'resolution': resolution_text,
                                'best_resolution': best_res,
                                'status': "Working"
                            })
                    else:
                        cap.release()
            except:
                pass

        # If no cameras found with default backend, try DirectShow
        if not working_cameras:
            for i in range(5):
                try:
                    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            cap.release()

                            # Test for best resolution with DirectShow
                            best_res = self._test_camera_resolutions(i, cv2.CAP_DSHOW)
                            if best_res:
                                width, height = best_res
                                resolution_text = f"{width}x{height} (Compatible)"

                                working_cameras.append({
                                    'index': i,
                                    'name': f"Camera {i} (DirectShow)",
                                    'resolution': resolution_text,
                                    'best_resolution': best_res,
                                    'status': "Working"
                                })
                        else:
                            cap.release()
                except:
                    pass

        # Update UI in main thread
        self.root.after(0, self._update_camera_list, working_cameras)

    def _update_camera_list(self, cameras):
        self.available_cameras = cameras

        if not cameras:
            self.camera_tree.insert("", "end", text="No cameras found",
                                   values=("-", "Not Available", "-"))
            self.status_label.config(text="❌ No working cameras detected. Check connections.", fg="red")
        else:
            for camera in cameras:
                self.camera_tree.insert("", "end", text=camera['name'],
                                       values=(camera['index'], camera['status'], camera['resolution']))
            self.status_label.config(text=f"✅ Found {len(cameras)} working camera(s). Select one to continue.", fg="green")

        self.refresh_btn.config(state="normal")

    def on_camera_select(self, event):
        selection = self.camera_tree.selection()
        if selection and self.available_cameras:
            item = self.camera_tree.item(selection[0])
            try:
                camera_index = int(item['values'][0])
                self.selected_camera = camera_index

                # Find the camera info to get its best resolution
                camera_info = next((cam for cam in self.available_cameras if cam['index'] == camera_index), None)
                if camera_info and 'best_resolution' in camera_info:
                    self.selected_camera_resolution = camera_info['best_resolution']
                else:
                    self.selected_camera_resolution = (640, 480)  # Fallback

                self.test_btn.config(state="normal")
                self.start_btn.config(state="normal")

                width, height = self.selected_camera_resolution
                self.status_label.config(
                    text=f"Selected camera {camera_index} at {width}x{height}. Click 'Start Recognition' to begin.",
                    fg="green"
                )
            except (ValueError, IndexError):
                self.selected_camera = None
                self.selected_camera_resolution = None
                self.test_btn.config(state="disabled")
                self.start_btn.config(state="disabled")

    def test_camera(self):
        if self.selected_camera is None:
            return

        if self.preview_running:
            self._stop_preview()
            return

        self._start_preview()

    def _start_preview(self):
        try:
            self.preview_cap = cv2.VideoCapture(self.selected_camera)
            if not self.preview_cap.isOpened():
                messagebox.showerror("Error", f"Cannot open camera {self.selected_camera}")
                return

            self.preview_running = True
            self.test_btn.config(text="⏹️ Stop Test")

            # Start preview in separate thread
            thread = threading.Thread(target=self._preview_loop)
            thread.daemon = True
            thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to test camera: {e}")

    def _preview_loop(self):
        cv2.namedWindow(f"Camera {self.selected_camera} Test", cv2.WINDOW_AUTOSIZE)

        while self.preview_running:
            ret, frame = self.preview_cap.read()
            if not ret:
                break

            # Add text overlay
            cv2.putText(frame, f"Camera {self.selected_camera} Test Preview",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press any key or close window to stop",
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

            cv2.imshow(f"Camera {self.selected_camera} Test", frame)

            if cv2.waitKey(1) & 0xFF != 255:  # Any key pressed
                break

        self._stop_preview()

    def _stop_preview(self):
        self.preview_running = False
        if self.preview_cap:
            self.preview_cap.release()
        cv2.destroyAllWindows()
        self.test_btn.config(text="👁️ Test Camera")

    def start_recognition(self):
        if self.selected_camera is None:
            messagebox.showwarning("Warning", "Please select a camera first.")
            return

        self._stop_preview()  # Stop any running preview
        self.root.quit()  # Close the selection window

    def get_selected_camera(self):
        return self.selected_camera, self.selected_camera_resolution

    def run(self):
        self.root.mainloop()
        return self.selected_camera, self.selected_camera_resolution

def select_camera():
    """
    Show camera selection dialog and return selected camera index and resolution.
    Returns (None, None) if user cancelled or no camera selected.
    """
    selector = CameraSelector()
    return selector.run()