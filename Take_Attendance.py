import time
import numpy as np
import cv2
import face_recognition
from pymongo import MongoClient
from tkinter import messagebox
from datetime import datetime

# Assuming MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['attendance_system']
faces_collection = db['faces']  # Collection storing student face encodings

def take_attendance(subject_code, section, roll_no):
    # Fetch stored face encodings for the given roll number from the database
    face_record = faces_collection.find_one({'roll_no': roll_no})
    
    if face_record is None or 'face_encoding' not in face_record:
        messagebox.showerror("Error", "No face data found for this roll number.")
        return

    # Load the stored face encoding for the given roll number
    stored_face_encoding = np.array(face_record['face_encoding'])

    cam = cv2.VideoCapture(0)
    recognized = False
    start_time = time.time()

    while True:
        ret, frame = cam.read()
        if not ret:
            messagebox.showerror("Error", "Camera not detected!")
            break

        # Convert the frame to RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame)

        if not face_locations:
            messagebox.showinfo("Info", "No face detected! Please face the camera.")
            continue  # Capture next frame

        # Get face encodings for the detected face(s)
        current_face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if current_face_encodings:
            current_face_encoding = current_face_encodings[0]  # First face detected

            # Compare the detected face with the stored face encoding from the database
            matches = face_recognition.compare_faces([stored_face_encoding], current_face_encoding, tolerance=0.4)

            # Check if any match was found
            if True in matches:
                recognized = True
                break
        else:
            messagebox.showerror("Error", "Face detected, but encoding not found! Please try again.")
            continue

        cv2.imshow("Taking Attendance", frame)

        # Timeout after 10 seconds
        elapsed_time = time.time() - start_time
        if elapsed_time > 10:
            messagebox.showerror("Error", "Face not recognized within 10 seconds! Exiting.")
            break

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to cancel
            break

    cam.release()
    cv2.destroyAllWindows()

    if recognized:
        # Mark attendance in the database
        attendance_data = {
            'roll_no': roll_no,
            'subject_code': subject_code,
            'section': section,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        db['attendance'].insert_one(attendance_data)
        messagebox.showinfo("Success", f"Attendance marked for Roll No: {roll_no}")
    else:
        messagebox.showerror("Error", "Face not matched!")
