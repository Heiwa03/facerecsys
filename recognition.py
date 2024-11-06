import cv2
import mediapipe as mp
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import subprocess
import platform

if platform.system() == "Darwin":
    import AVFoundation # For macOS

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class Recognition:
    def __init__(self):
        self.face_mesh_live = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=5)  
        self.face_mesh_static = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=5)  
        self.face_mesh_alt = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.cap = None
        self.timer = None
        self.use_alt = False

    def is_running(self):
        return self.cap is not None

    def list_available_cameras(self):
        if platform.system() == "Windows":
            return self.list_available_cameras_windows()
        elif platform.system() == "Linux":
            return self.list_available_cameras_linux()
        elif platform.system() == "Darwin":
            return self.list_available_cameras_macos()
        else:
            return []

    def list_available_cameras_windows(self):
        index = 0
        camera_indices = []
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                camera_indices.append(index)
            cap.release()
            index += 1
        return camera_indices

    def list_available_cameras_linux(self):
        try:
            output = subprocess.check_output("v4l2-ctl --list-devices", shell=True).decode()
            devices = output.split("\n\n")
            camera_indices = []
            for device in devices:
                lines = device.split("\n")
                if len(lines) > 1:
                    for line in lines[1:]:
                        if "/dev/video" in line:
                            index = int(line.split("/dev/video")[1])
                            camera_indices.append(index)
            return camera_indices
        except subprocess.CalledProcessError:
            return []

    def list_available_cameras_macos(self):
        devices = AVFoundation.AVCaptureDevice.devicesWithMediaType_(AVFoundation.AVMediaTypeVideo)
        camera_indices = [i for i, _ in enumerate(devices)]
        return camera_indices
    
    def start_face_recognition(self, video_label, camera_index, use_alt=False):
        self.cap = cv2.VideoCapture(camera_index)
        self.use_alt = use_alt
        self.timer = QTimer()
        if use_alt:
            self.timer.timeout.connect(lambda: self.alt_update_frame(video_label))
        else:
            self.timer.timeout.connect(lambda: self.update_frame(video_label))
        self.timer.start(30)

    def update_frame(self, video_label):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.resize(frame, (1366, 768))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame_rgb.shape
        results = self.face_mesh_live.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        video_label.setPixmap(QPixmap.fromImage(q_image))

    def alt_update_frame(self, video_label):
        ret, image = self.cap.read()
        if not ret:
            return
        frame = cv2.resize(frame, (1366, 768))
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh_alt.process(image)

        # Draw the face mesh annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style())
        # Flip the image horizontally for a selfie-view display.
        frame = image
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        video_label.setPixmap(QPixmap.fromImage(q_image))

    def stop_recognition(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.timer is not None:
            self.timer.stop()
            self.timer = None

    def process_uploaded_photo(self, file_path, video_label):
        image = cv2.imread(file_path)
        if image is None:
            return

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = image_rgb.shape
        results = self.face_mesh_static.process(image_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(image, (x, y), 1, (0, 255, 0), -1)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        bytes_per_line = ch * w
        q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        video_label.setPixmap(QPixmap.fromImage(q_image))