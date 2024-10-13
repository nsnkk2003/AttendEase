import cv2
import face_recognition
import numpy as np
from datetime import datetime
from pymongo import MongoClient
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd

# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')  # Your MongoDB connection string
db = client['smart_attendance_system']  # Database name
faces_collection = db['faces']  # Collection for faces
students_collection = db['students']  # Collection for students

# Register student function
def register_student(roll_no, name, year, section):
    # Check if the roll number already exists
    if students_collection.find_one({'roll_no': roll_no}):
        messagebox.showerror("Error", f"Roll number {roll_no} is already registered.")
        return

    # Initialize the webcam and capture face encodings
    cam = cv2.VideoCapture(0)
    face_encodings = []

    messagebox.showinfo("Info", "Please face the camera for automatic registration. It will capture your face multiple times.")

    while len(face_encodings) < 10:  # Automatically capture 10 face encodings
        ret, frame = cam.read()
        if not ret:
            messagebox.showerror("Error", "Camera not detected!")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        if face_locations:
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            face_encodings.append(face_encoding)
            cv2.imshow("Registering Face", frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to cancel registration
            break

    cam.release()
    cv2.destroyAllWindows()

    if len(face_encodings) == 10:
        # Store student data in MongoDB
        student_data = {'roll_no': roll_no, 'name': name, 'year': year, 'section': section}
        students_collection.insert_one(student_data)

        # Store face encodings in MongoDB
        for encoding in face_encodings:
            faces_collection.insert_one({'roll_no': roll_no, 'face_encoding': encoding.tolist()})

        messagebox.showinfo("Success", f"Student {name} registered successfully!")
    else:
        messagebox.showerror("Error", "Failed to capture enough face data for registration.")

# Attendance function with subject-based roll number verification
def take_attendance(subject_code, roll_no):
    # Fetch stored face encodings for the given roll number
    face_record = faces_collection.find_one({'roll_no': roll_no})

    if face_record is None or 'face_encoding' not in face_record:
        messagebox.showerror("Error", "No face data found for this roll number.")
        return

    # Load the face encodings from MongoDB
    face_encodings = np.array(face_record['face_encoding'])

    cam = cv2.VideoCapture(0)
    recognized = False

    messagebox.showinfo("Info", "Please face the camera for attendance verification.")

    while True:
        ret, frame = cam.read()
        if not ret:
            messagebox.showerror("Error", "Camera not detected!")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        if face_locations:
            current_face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            matches = face_recognition.compare_faces([face_encodings], current_face_encoding)

            if True in matches:
                recognized = True
                break

        cv2.imshow("Taking Attendance", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to cancel
            break

    cam.release()
    cv2.destroyAllWindows()

    if recognized:
        attendance_data = {
            'roll_no': roll_no,
            'subject_code': subject_code,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        db['attendance'].insert_one(attendance_data)
        messagebox.showinfo("Success", f"Attendance marked for Roll No: {roll_no} in {subject_code}.")
    else:
        messagebox.showerror("Error", "Face not matched!")

# Export attendance function
def export_attendance(section):
    attendance_data = list(db['attendance'].find({'section': section}))
    if not attendance_data:
        messagebox.showerror("Error", f"No attendance records found for section {section}.")
        return

    df = pd.DataFrame(attendance_data)
    file_name = f"attendance_{section}_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    df.to_excel(file_name, index=False)
    messagebox.showinfo("Success", f"Attendance exported to {file_name}")

# GUI for Taking Attendance and Registering Students
def main_menu():
    window = tk.Tk()
    window.title("Smart Attendance System")

    # Registration section
    reg_label = tk.Label(window, text="Register Student")
    reg_label.pack()

    reg_roll_label = tk.Label(window, text="Roll No:")
    reg_roll_label.pack()
    reg_roll_entry = tk.Entry(window)
    reg_roll_entry.pack()

    reg_name_label = tk.Label(window, text="Name:")
    reg_name_label.pack()
    reg_name_entry = tk.Entry(window)
    reg_name_entry.pack()

    reg_year_label = tk.Label(window, text="Year:")
    reg_year_label.pack()
    reg_year_entry = tk.Entry(window)
    reg_year_entry.pack()

    reg_section_label = tk.Label(window, text="Section:")
    reg_section_label.pack()
    reg_section_entry = tk.Entry(window)
    reg_section_entry.pack()

    def on_register():
        roll_no = reg_roll_entry.get()
        name = reg_name_entry.get()
        year = reg_year_entry.get()
        section = reg_section_entry.get()
        register_student(roll_no, name, year, section)

    register_btn = tk.Button(window, text="Register", command=on_register)
    register_btn.pack()

    # Attendance section
    att_label = tk.Label(window, text="Take Attendance")
    att_label.pack()

    att_roll_label = tk.Label(window, text="Roll No:")
    att_roll_label.pack()
    att_roll_entry = tk.Entry(window)
    att_roll_entry.pack()

    att_subject_label = tk.Label(window, text="Select Subject:")
    att_subject_label.pack()
    subject_var = tk.StringVar()
    subjects = ["OS", "CNN", "DBMS", "Java"]
    subject_dropdown = ttk.Combobox(window, textvariable=subject_var, values=subjects)
    subject_dropdown.pack()

    def on_attendance():
        roll_no = att_roll_entry.get()
        subject_code = subject_var.get()
        take_attendance(subject_code, roll_no)

    attendance_btn = tk.Button(window, text="Take Attendance", command=on_attendance)
    attendance_btn.pack()

    # Export section
    export_label = tk.Label(window, text="Export Attendance")
    export_label.pack()

    export_section_label = tk.Label(window, text="Section:")
    export_section_label.pack()
    export_section_entry = tk.Entry(window)
    export_section_entry.pack()

    def on_export():
        section = export_section_entry.get()
        export_attendance(section)

    export_btn = tk.Button(window, text="Export Attendance", command=on_export)
    export_btn.pack()

    window.mainloop()

# Run the main menu
if __name__ == "__main__":
    main_menu()
