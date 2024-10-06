import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import Label, OptionMenu, StringVar
from PIL import Image, ImageTk

# Global variable for capturing video
cap = None

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
# Set `max_num_faces` to a higher value to allow detection of multiple faces
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=5, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# Function to start video capture and face mesh detection
def start_recognition(camera_index):
    global cap
    cap = cv2.VideoCapture(int(camera_index))

    def update_frame():
        if cap is not None:
            ret, frame = cap.read()
            if ret:
                # Convert the image to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Process the image to find face mesh
                results = face_mesh.process(rgb_frame)

                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        # Draw face mesh for each detected face
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_TESSELATION,
                            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=1)
                        )

                # Convert the image for Tkinter display
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=img)
                lbl_video.imgtk = imgtk
                lbl_video.configure(image=imgtk)

            lbl_video.after(10, update_frame)

    update_frame()

# Function to stop video capture
def stop_recognition():
    global cap
    if cap is not None:
        cap.release()
        cap = None

# Create Tkinter window
root = tk.Tk()
root.title("Real-Time Face Mesh Detection")

# Video display label
lbl_video = Label(root)
lbl_video.pack()

# Camera selection
camera_var = StringVar(root)
camera_var.set("0")

# Camera selection menu
camera_menu = OptionMenu(root, camera_var, "0", "1", "2", "3")
camera_menu.pack()

# Stop button
btn_stop = tk.Button(root, text="Stop Recognition", command=stop_recognition)
btn_stop.pack()

# Automatically start recognition after the window is created
start_recognition(camera_var.get())

# Start the Tkinter event loop
root.mainloop()
