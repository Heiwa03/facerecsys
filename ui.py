import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from recognition import Recognition

# Constants for styles
MODERN_STYLE = """
    QWidget {
        background-color: #2E2E2E;
        color: #FFFFFF;
        font-family: Cascadia Code;
        font-size: 14px;
    }
    QLabel {
        border: 2px solid green;
        border-radius: 4px;
        padding: 2px;
        font-size: 18px;
        color: #FFFFFF;
    }
    QComboBox {
        font-size: 18px;
        padding: 5px;
        background-color: #3E3E3E;
        color: #FFFFFF;
        border: 1px solid #5E5E5E;
        border-radius: 5px;
    }
    QPushButton {
        font-size: 18px;
        padding: 10px;
        background-color: #4CAF50;
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #45A049;
    }
    QPushButton:pressed {
        background-color: #3E8E41;
    }
"""

class FaceRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.recognition = Recognition()
        self.initUI()
        self.update_camera_list()  # Populate the camera list on startup

    def initUI(self):
        """Initialize the main UI components."""
        self.setWindowTitle("Face Recognition")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(MODERN_STYLE)

        self.layout = QVBoxLayout()

        self.init_video_label()
        self.init_camera_combo_box()
        self.init_buttons()

        self.setLayout(self.layout)

        # Add fade-in animation for the video label
        self.fade_in_animation(self.video_label)

    def init_video_label(self):
        """Initialize the video label for displaying video feed or uploaded image."""
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.video_label)

    def init_camera_combo_box(self):
        """Initialize the camera selection combo box."""
        self.camera_combo_box = QComboBox(self)
        self.layout.addWidget(self.camera_combo_box)

    def init_buttons(self):
        """Initialize the control buttons."""
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Recognition", self)
        self.start_button.setIcon(QIcon("icons/start.png"))
        self.start_button.clicked.connect(self.start_recognition)
        self.start_button.setVisible(True)  # Show the start button initially
        button_layout.addWidget(self.start_button)

        self.alt_start_button = QPushButton("Start Alt Recognition", self)
        self.alt_start_button.setIcon(QIcon("icons/start.png"))
        self.alt_start_button.clicked.connect(self.start_alt_recognition)
        self.alt_start_button.setVisible(True)  # Show the alt start button initially
        button_layout.addWidget(self.alt_start_button)

        self.stop_button = QPushButton("Stop Recognition", self)
        self.stop_button.setIcon(QIcon("icons/stop.png"))
        self.stop_button.clicked.connect(self.stop_recognition)
        self.stop_button.setVisible(False)  # Hide the stop button initially
        button_layout.addWidget(self.stop_button)

        self.upload_button = QPushButton("Upload Photo", self)
        self.upload_button.setIcon(QIcon("icons/upload.png"))
        self.upload_button.clicked.connect(self.upload_photo)
        button_layout.addWidget(self.upload_button)

        self.layout.addLayout(button_layout)

        # Add hover animation for buttons
        self.add_hover_animation(self.start_button)
        self.add_hover_animation(self.alt_start_button)
        self.add_hover_animation(self.stop_button)
        self.add_hover_animation(self.upload_button)

    def update_camera_list(self):
        """Update the camera list in the combo box."""
        available_cameras = self.recognition.list_available_cameras()
        self.camera_combo_box.clear()
        for camera_index in available_cameras:
            self.camera_combo_box.addItem(f"Camera {camera_index}", camera_index)

    def start_recognition(self):
        """Start the face recognition process."""
        self.start_button.setVisible(False)
        self.alt_start_button.setVisible(False)
        self.stop_button.setVisible(True)
        selected_camera_index = self.camera_combo_box.currentData()
        self.recognition.start_face_recognition(self.video_label, selected_camera_index)

    def start_alt_recognition(self):
        """Start the alternative face recognition process."""
        self.start_button.setVisible(False)
        self.alt_start_button.setVisible(False)
        self.stop_button.setVisible(True)
        selected_camera_index = self.camera_combo_box.currentData()
        self.recognition.start_face_recognition(self.video_label, selected_camera_index, use_alt=True)

    def stop_recognition(self):
        """Stop the face recognition process."""
        self.stop_button.setVisible(False)
        self.start_button.setVisible(True)
        self.alt_start_button.setVisible(True)
        self.recognition.stop_recognition()

    def upload_photo(self):
        """Upload a photo and process it for face recognition."""
        # Stop live recognition if it's active
        if self.recognition.is_running():
            self.stop_recognition()
        
        # Open file dialog to select an image
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            # Display the uploaded photo with face landmarks
            self.recognition.process_uploaded_photo(file_path, self.video_label)

    def fade_in_animation(self, widget):
        """Add a fade-in animation to the specified widget."""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(1000)
        animation.setStartValue(QRect(widget.x(), widget.y(), widget.width(), 0))
        animation.setEndValue(QRect(widget.x(), widget.y(), widget.width(), widget.height()))
        animation.start()

    def add_hover_animation(self, button):
        """Add a hover animation to the specified button."""
        button.installEventFilter(self)

    def eventFilter(self, source, event):
        """Event filter to handle hover animations."""
        if event.type() == event.Enter and isinstance(source, QPushButton):
            self.animate_button(source, 1.1)
        elif event.type() == event.Leave and isinstance(source, QPushButton):
            self.animate_button(source, 1.0)
        return super().eventFilter(source, event)

    def animate_button(self, button, scale_factor):
        """Animate the button size."""
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        rect = button.geometry()
        new_width = int(rect.width() * scale_factor)
        new_height = int(rect.height() * scale_factor)
        new_rect = QRect(rect.x(), rect.y(), new_width, new_height)
        animation.setStartValue(rect)
        animation.setEndValue(new_rect)
        animation.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec_())