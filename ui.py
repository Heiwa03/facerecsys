import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from recognition import Recognition

class FaceRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.recognition = Recognition()
        self.initUI()
        self.start_recognition()  # Pornește captarea live automat la rularea aplicației

    def initUI(self):
        self.setWindowTitle("Face Recognition")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        # Video label for displaying video feed or uploaded image
        self.video_label = QLabel(self)
        self.layout.addWidget(self.video_label)

        # Start Recognition button
        self.start_button = QPushButton("Start Recognition", self)
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 24px; 
                background-color: green; 
                color: white;
            }
            QPushButton:hover {
                font-size: 24px; 
                background-color: darkGreen; 
                color: white;
            }
        """)
        self.start_button.clicked.connect(self.start_recognition)
        self.start_button.setVisible(False)  # Ascunde butonul, deoarece captarea este deja pornită
        self.layout.addWidget(self.start_button)

        # Stop Recognition button
        self.stop_button = QPushButton("Stop Recognition", self)
        self.stop_button.setStyleSheet("""
            QPushButton {
                font-size: 24px; 
                background-color: red; 
                color: white;
            }
            QPushButton:hover {
                font-size: 24px; 
                background-color: darkRed; 
                color: white;
            }
            
        """)
        self.stop_button.clicked.connect(self.stop_recognition)
        self.stop_button.setVisible(True)
        self.layout.addWidget(self.stop_button)

        # Upload Photo button
        self.upload_button = QPushButton("Upload Photo", self)
        self.upload_button.setStyleSheet("""
            QPushButton {
                font-size: 24px; 
                background-color: blue; 
                color: white;
            }
            QPushButton:hover {
                font-size: 24px; 
                background-color: darkBlue; 
                color: white;
                
            }
        """)
        self.upload_button.clicked.connect(self.upload_photo)
        self.layout.addWidget(self.upload_button)

        self.setLayout(self.layout)

    def start_recognition(self):
        self.start_button.setVisible(False)
        self.stop_button.setVisible(True)
        self.recognition.start_face_recognition(self.video_label)

    def stop_recognition(self):
        self.stop_button.setVisible(False)
        self.start_button.setVisible(True)
        self.recognition.stop_recognition()

    def upload_photo(self):
        # Stop live recognition if it's active
        if self.recognition.is_running():
            self.stop_recognition()
        
        # Open file dialog to select an image
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            # Display the uploaded photo with face landmarks
            self.recognition.process_uploaded_photo(file_path, self.video_label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec_())
    