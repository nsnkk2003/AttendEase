import cv2
import numpy as np
import os
import dlib
import firebase_admin
from firebase_admin import credentials, db
from tkinter import messagebox
import csv

# Initialize Firebase Admin SDK
cred = credentials.Certificate("attendease-90f2d-firebase-adminsdk-811vx-15ca6d290e.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://attendease-90f2d-default-rtdb.firebaseio.com/'
})

# Paths to models and encoding folder
PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
RECOGNIZER_PATH = "dlib_face_recognition_resnet_model_v1.dat"

# Load Dlib models
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)
recognizer = dlib.face_recognition_model_v1(RECOGNIZER_PATH)

# Constants for subjects
DBMS = 'DBMS'
OS = 'OS'
CS = 'CS'
ASN = 'ASN'

# Function to extract face encoding
def extract_face_encoding(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    
    if len(faces) == 0:
        return None

    face = faces[0]  # Get the first face detected
    shape = predictor(gray, face)  # Get facial landmarks
    face_encoding = np.array(recognizer.compute_face_descriptor(image, shape))  # Get the 128D face encoding
    return face_encoding

# Register a student's face and store info in Firebase
def register_student(roll_no, name):
    cap = cv2.VideoCapture(0)
    angles = ['front', 'left', 'right', 'up', 'down']
    face_samples = []

    messagebox.showinfo("Instructions", "Please look at the camera and follow the prompts to take pictures.")

    for angle in angles:
        messagebox.showinfo("Capture", f"Position your face {angle} and press Enter.")
        
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image. Exiting...")
            break

        # Extract and save the face encoding (skip saving the photo)
        encoding = extract_face_encoding(frame)
        if encoding is not None:
            face_samples.append(encoding)
        else:
            messagebox.showwarning("Warning", f"No face detected in the {angle} view.")

    cap.release()
    cv2.destroyAllWindows()

    if face_samples:
        # Store face encodings in Firebase
        try:
            student_ref = db.reference(f'encodings/{roll_no}')
            for i, encoding in enumerate(face_samples):
                student_ref.child(f'encoding_{i}').set(encoding.tolist())  # Convert numpy array to list
            
            # Insert student info in Firebase (name, roll_no, and attendance)
            attendance_ref = db.reference('attendance')
            attendance_ref.child(roll_no).set({
                'name': name,
                DBMS: 0,  # Change to uppercase
                OS: 0,    # Change to uppercase
                CS: 0,    # Change to uppercase
                ASN: 0,   # Change to uppercase
                'present_classes': 0
            })
            messagebox.showinfo("Success", f"Successfully registered {name} with Roll No {roll_no}!")
        except Exception as err:
            messagebox.showerror("Error", f"Firebase error: {err}")
    else:
        messagebox.showerror("Error", f"Failed to capture valid face encodings for {name}.")

# Start a class and increment total classes
def start_class(subject):
    try:
        attendance_ref = db.reference('classes').child(subject)
        current_classes = attendance_ref.get()

        if current_classes is None:
            attendance_ref.set(1)  # Initialize if it doesn't exist
        else:
            attendance_ref.set(current_classes + 1)  # Increment existing count

        messagebox.showinfo("Success", f"Started {subject} class. Total classes incremented.")
    except Exception as err:
        messagebox.showerror("Error", f"Firebase error: {err}")

# Verify and mark attendance
def mark_attendance(roll_no, subject):
    try:
        # Retrieve encodings from Firebase
        encodings_ref = db.reference(f'encodings/{roll_no}')
        encodings = encodings_ref.get()

        if not encodings:
            messagebox.showerror("Error", f"No encodings found for Roll No {roll_no}. Please register first.")
            return

        encodings = [np.array(enc) for enc in encodings.values()]  # Convert back to numpy arrays

        cap = cv2.VideoCapture(0)
        messagebox.showinfo("Attendance", "Please look at the camera to verify your identity.")

        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image. Exiting...")
            cap.release()
            return

        captured_encoding = extract_face_encoding(frame)
        
        if captured_encoding is None:
            messagebox.showerror("Error", "No face detected in the captured image.")
            cap.release()
            return

        for stored_encoding in encodings:
            distance = np.linalg.norm(captured_encoding - stored_encoding)
            if distance < 0.5:  # Threshold for face recognition
                try:
                    # Increment present classes for the subject
                    attendance_ref = db.reference('attendance').child(roll_no).child(subject)
                    current_attendance = attendance_ref.get()

                    if current_attendance is None:
                        attendance_ref.set(1)  # Initialize if it doesn't exist
                    else:
                        attendance_ref.set(current_attendance + 1)  # Increment existing attendance

                    # Increment total present classes
                    total_classes_ref = db.reference('attendance').child(roll_no).child('present_classes')
                    current_total_classes = total_classes_ref.get()

                    if current_total_classes is None:
                        total_classes_ref.set(1)  # Initialize if it doesn't exist
                    else:
                        total_classes_ref.set(current_total_classes + 1)  # Increment existing total classes

                    messagebox.showinfo("Success", f"Attendance marked for {roll_no} in {subject}!")
                    cap.release()
                    return
                except Exception as err:
                    messagebox.showerror("Error", f"Firebase error: {err}")
                    cap.release()
                    return

        messagebox.showerror("Error", "Verification failed! Face not recognized.")
        cap.release()

    except Exception as err:
        messagebox.showerror("Error", f"Firebase error: {err}")

def export_full_attendance_percentages():
    try:
        # Fetch attendance data from Firebase
        attendance_ref = db.reference('attendance')
        attendance_data = attendance_ref.get()

        # Debugging: Check what data is fetched
        print("Attendance Data:", attendance_data)

        if not attendance_data:
            messagebox.showinfo("Export Attendance", "No attendance data available.")
            return

        # Handle both dictionary and list structures
        if isinstance(attendance_data, dict):
            students = attendance_data.items()  # If it's a dictionary, iterate over items
        elif isinstance(attendance_data, list):
            students = enumerate(attendance_data)  # If it's a list, iterate using an index
        else:
            messagebox.showerror("Export Attendance", "Invalid attendance data format.")
            return

        # Prepare CSV data
        csv_data = []
        header = ['Roll No', 'Name', 'DBMS Attendance (%)', 'OS Attendance (%)', 'CS Attendance (%)', 'ASN Attendance (%)']
        csv_data.append(header)

        # Fetch class data
        classes_ref = db.reference('classes')
        classes_data = classes_ref.get()

        # Debugging: Check what class data is fetched
        print("Classes Data:", classes_data)

        # Default values for classes if not found
        dbms_classes = classes_data.get(DBMS, 1) if classes_data else 1  # To avoid division by zero
        os_classes = classes_data.get(OS, 1) if classes_data else 1
        cs_classes = classes_data.get(CS, 1) if classes_data else 1
        asn_classes = classes_data.get(ASN, 1) if classes_data else 1

        # Extracting attendance details for each student
        for roll_no, student_data in students:
            if student_data is None:  # Skip if no student data is found
                continue

            name = student_data.get('name', 'Unknown')

            # Calculate percentages
            dbms_attendance = student_data.get(DBMS, 0)
            os_attendance = student_data.get(OS, 0)
            cs_attendance = student_data.get(CS, 0)
            asn_attendance = student_data.get(ASN, 0)

            dbms_percentage = (dbms_attendance / dbms_classes) * 100
            os_percentage = (os_attendance / os_classes) * 100
            cs_percentage = (cs_attendance / cs_classes) * 100
            asn_percentage = (asn_attendance / asn_classes) * 100

            csv_data.append([
                roll_no,
                name,
                round(dbms_percentage, 2),
                round(os_percentage, 2),
                round(cs_percentage, 2),
                round(asn_percentage, 2)
            ])

        # Define the CSV file path
        csv_file_path = "attendance_percentages.csv"
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(csv_data)

        messagebox.showinfo("Export Attendance", f"Attendance percentages exported to {csv_file_path} successfully!")

    except Exception as e:
        messagebox.showerror("Export Attendance", f"Error exporting attendance: {str(e)}")

# Note: Ensure that the necessary UI components and main loop are implemented to call these functions as required.
