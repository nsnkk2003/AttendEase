def register_student(roll_no, name, year, section):
    # Check if the roll number already exists
    if students_collection.find_one({'roll_no': roll_no}):
        messagebox.showerror("Error", f"Roll number {roll_no} is already registered.")
        return

    # Initialize the webcam and capture face encodings
    cam = cv2.VideoCapture(0)
    face_encodings = []

    messagebox.showinfo("Info", "Capturing images now. Please face the camera. This will capture multiple images.")
    
    # Automatically capture 5-6 face encodings
    for i in range(5):  # Capture 5 images
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
            cv2.waitKey(1000)  # Wait for 1 second between captures

    cam.release()
    cv2.destroyAllWindows()

    if len(face_encodings) == 5:
        # Store student data in MongoDB
        student_data = {'roll_no': roll_no, 'name': name, 'year': year, 'section': section}
        students_collection.insert_one(student_data)

        # Store face encodings in MongoDB
        for encoding in face_encodings:
            faces_collection.insert_one({'roll_no': roll_no, 'face_encoding': encoding.tolist()})

        messagebox.showinfo("Success", f"Student {name} registered successfully!")
    else:
        messagebox.showerror("Error", "Failed to capture enough face data for registration.")
