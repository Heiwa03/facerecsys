import cv2
import mediapipe as mp
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

mp_face_mesh = mp.solutions.face_mesh

class Recognition:
    def __init__(self):
        self.face_mesh_live = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=5)  
        self.face_mesh_static = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=5)  
        self.cap = None
        self.timer = None

    def is_running(self):
        return self.cap is not None

    def start_face_recognition(self, video_label):
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update_frame(video_label))
        self.timer.start(30)

    def update_frame(self, video_label):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh_live.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

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
        results = self.face_mesh_static.process(image_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * image.shape[1])
                    y = int(landmark.y * image.shape[0])
                    cv2.circle(image, (x, y), 1, (0, 255, 0), -1)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        bytes_per_line = ch * w
        q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        video_label.setPixmap(QPixmap.fromImage(q_image))
