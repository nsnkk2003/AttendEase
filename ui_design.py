import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QLineEdit, QComboBox, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, QDateTime
from app import register_student, start_class, mark_attendance, export_full_attendance_percentages  # Import your functions

class AttendeaseMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attendease")
        self.setGeometry(100, 100, 1440, 1024)  # Set the window size directly
        self.background_label = QLabel(self)

        # Set the background image
        self.set_background_image("Desktop2.png")  # Ensure the path is correct

        # Create buttons on the left side
        self.create_buttons()

        # Placeholder widget for input forms
        self.form_container = QWidget(self)
        self.form_container.setGeometry(750, 200, 600, 600)  # Adjusted position to the right by 150 pixels
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_container.setLayout(self.form_layout)
        self.form_container.setStyleSheet("background-color: #000000; border-radius: 15px;")  # Dark black background
        self.form_container.hide()  # Hide initially
        self.add_date_time_label()


    def set_background_image(self, image_path):
        background_pixmap = QPixmap(image_path)
        if background_pixmap.isNull():
            self.show_message("Failed to load background image. Check the file path.", error=True)
            self.setStyleSheet("background-color: lightgray;")  # Fallback background color
            return
        self.background_label.setPixmap(background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, self.width(), self.height())

    def create_buttons(self):
        button_style = """
            QPushButton {
                font-family: 'Segoe UI';
                font-size: 15pt;
                font-weight: bold;
                text-transform: uppercase;
                color: white;
                background-color: black;
                border: none;  /* Removed white border */
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """
        button_texts = ["Register Student", "Start Class", "Mark Attendance", "Export Attendance"]
        button_height = 50
        spacing = 20

        for i, text in enumerate(button_texts):
            button = QPushButton(text, self)
            button.setStyleSheet(button_style)
            button.setGeometry(40, 250 + i * (button_height + spacing), 300, button_height)  # Fixed positioning
            button.clicked.connect(lambda _, t=text: self.show_form(t))  # Show form based on button

    def show_form(self, form_type):
        # Clear any previous inputs safely
        while self.form_layout.count():
            widget = self.form_layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()  # Ensure proper cleanup

        # Show relevant form based on button clicked
        if form_type == "Register Student":
            self.display_register_form()
        elif form_type == "Start Class":
            self.display_start_class_form()
        elif form_type == "Mark Attendance":
            self.display_mark_attendance_form()
        elif form_type == "Export Attendance":
            self.display_export_form()
        
        self.form_container.show()  # Show the form container

    def display_register_form(self):
        title = QLabel("REGISTER STUDENT")
        title.setStyleSheet("font-size: 24pt; color: white; text-align: center;")  # Title in uppercase
        title.setAlignment(Qt.AlignCenter)
        
        roll_no_input = QLineEdit()
        roll_no_input.setPlaceholderText("Roll Number")
        roll_no_input.setStyleSheet("font-size: 18pt; color: white; background-color: #555555; padding: 10px; border-radius: 10px;")

        name_input = QLineEdit()
        name_input.setPlaceholderText("Student Name")
        name_input.setStyleSheet("font-size: 18pt; color: white; background-color: #555555; padding: 10px; border-radius: 10px;")

        register_button = QPushButton("REGISTER")
        register_button.setFixedHeight(50)  # Uniform height
        register_button.setStyleSheet("font-size: 18pt; color: white; background-color: #008000; border-radius: 10px;")
        register_button.clicked.connect(lambda: register_student(roll_no_input.text(), name_input.text()))  # Call the imported function

        # Add to layout with spacing
        self.form_layout.addWidget(title)
        self.form_layout.addSpacing(20)  # Space before inputs

        # Center the input boxes
        self.form_layout.addWidget(roll_no_input)
        self.form_layout.addSpacing(10)  # Space between inputs
        self.form_layout.addWidget(name_input)
        self.form_layout.addSpacing(20)  # Space before button
        self.form_layout.addWidget(register_button)

        # Center the layout
        self.form_layout.setAlignment(Qt.AlignCenter)

    def display_start_class_form(self):
        title = QLabel("START CLASS")
        title.setStyleSheet("font-size: 24pt; color: white; text-align: center;")
        title.setAlignment(Qt.AlignCenter)

        subject_input = QComboBox()
        subject_input.addItems(["DBMS", "OS", "CS", "ASN"])
        subject_input.setStyleSheet("font-size: 18pt; color: white; background-color: #555555; padding: 10px; border-radius: 10px;")

        start_button = QPushButton("START CLASS")
        start_button.setFixedHeight(50)  # Uniform height
        start_button.setStyleSheet("font-size: 18pt; color: white; background-color: #008000; border-radius: 10px;")
        start_button.clicked.connect(lambda: start_class(subject_input.currentText()))  # Call the imported function

        # Add to layout with spacing
        self.form_layout.addWidget(title)
        self.form_layout.addSpacing(20)  # Space before input
        self.form_layout.addWidget(subject_input)
        self.form_layout.addSpacing(20)  # Space before button
        self.form_layout.addWidget(start_button)

        # Center the layout
        self.form_layout.setAlignment(Qt.AlignCenter)

    def display_mark_attendance_form(self):
        title = QLabel("MARK ATTENDANCE")
        title.setStyleSheet("font-size: 24pt; color: white; text-align: center;")
        title.setAlignment(Qt.AlignCenter)

        roll_no_input = QLineEdit()
        roll_no_input.setPlaceholderText("Roll Number")
        roll_no_input.setStyleSheet("font-size: 18pt; color: white; background-color: #555555; padding: 10px; border-radius: 10px;")

        subject_input = QComboBox()
        subject_input.addItems(["DBMS", "OS", "CS", "ASN"])
        subject_input.setStyleSheet("font-size: 18pt; color: white; background-color: #555555; padding: 10px; border-radius: 10px;")

        mark_button = QPushButton("MARK ATTENDANCE")
        mark_button.setFixedHeight(50)  # Uniform height
        mark_button.setStyleSheet("font-size: 18pt; color: white; background-color: #008000; border-radius: 10px;")
        mark_button.clicked.connect(lambda: mark_attendance(roll_no_input.text(), subject_input.currentText()))  # Call the imported function

        # Add to layout with spacing
        self.form_layout.addWidget(title)
        self.form_layout.addSpacing(20)  # Space before inputs
        self.form_layout.addWidget(roll_no_input)
        self.form_layout.addSpacing(10)  # Space between inputs
        self.form_layout.addWidget(subject_input)
        self.form_layout.addSpacing(20)  # Space before button
        self.form_layout.addWidget(mark_button)

        # Center the layout
        self.form_layout.setAlignment(Qt.AlignCenter)

    def display_export_form(self):
        title = QLabel("EXPORT ATTENDANCE")
        title.setStyleSheet("font-size: 24pt; color: white; text-align: center;")
        title.setAlignment(Qt.AlignCenter)

        export_button = QPushButton("EXPORT ATTENDANCE")
        export_button.setFixedHeight(50)  # Uniform height
        export_button.setStyleSheet("font-size: 18pt; color: white; background-color: #008000; border-radius: 10px;")
        export_button.clicked.connect(export_full_attendance_percentages)  # Call the imported function

        # Add to layout with spacing
        self.form_layout.addWidget(title)
        self.form_layout.addSpacing(20)  # Space before button
        self.form_layout.addWidget(export_button)

        # Center the layout
        self.form_layout.setAlignment(Qt.AlignCenter)

    def show_message(self, message, error=False):
        msg = QMessageBox()
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical if error else QMessageBox.Information)
        msg.setWindowTitle("Notification")
        msg.exec_()
    
    def add_date_time_label(self):
    # Label to display date and time
      self.date_time_label = QLabel(self)
      self.date_time_label.setStyleSheet("font-size: 16pt; color: white; background-color: black; padding: 5px; border-radius: 5px;")
      self.date_time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
      self.date_time_label.setGeometry(self.width() - 360, 10, 350, 40)  # Position at the top right

    # Timer to update the date and time
      self.timer = QTimer(self)
      self.timer.timeout.connect(self.update_date_time)
      self.timer.start(1000)  # Update every second

    # Initial date-time update
      self.update_date_time()


    def update_date_time(self):
      current_time = QDateTime.currentDateTime().toString("ddd, MMM dd yyyy - hh:mm:ss AP")
      self.date_time_label.setText(current_time)

    def resizeEvent(self, event):
      if hasattr(self, 'date_time_label'):
          self.date_time_label.setGeometry(self.width() - 360, 10, 350, 40)  # Adjust position
      if hasattr(self, 'background_label'):
          self.background_label.setGeometry(0, 0, self.width(), self.height())
      super().resizeEvent(event)
