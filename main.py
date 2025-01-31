import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
from ui_design import AttendeaseMainWindow  # Ensure ui_design.py contains AttendeaseMainWindow

# Global variable to retain reference to the main window
main_window = None

def show_splash_screen(app):
    try:
        # Load and scale the splash screen logo with a larger size
        splash_pix = QPixmap('logo-color.png').scaled(
            800, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        # Create splash widget with centered logo
        splash_widget = QWidget()
        splash_widget.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        splash_widget.setStyleSheet("background-color: white;")  # Background color for the splash screen

        # Set up centered layout for splash screen
        logo_label = QLabel(splash_widget)
        logo_label.setPixmap(splash_pix)
        logo_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(logo_label)
        splash_widget.setLayout(layout)
        splash_widget.setWindowIcon(QIcon('logo-color.ico'))

        splash_widget.showFullScreen()  # Display the splash screen in full-screen mode
        print("Splash screen displayed in full screen with larger centered logo.")

        # Show the main window after the splash screen delay
        splash_duration = 3000  # 3 seconds delay
        QTimer.singleShot(splash_duration, lambda: load_main_window(splash_widget))
    except Exception as e:
        print(f"Error showing splash screen: {e}")

def load_main_window(splash_widget):
    global main_window  # Keep a reference to ensure it stays open
    print("Closing splash screen and launching main window...")
    splash_widget.close()  # Close splash screen

    # Initialize and show the main Attendease window maximized (taskbar visible)
    main_window = AttendeaseMainWindow()
    main_window.showMaximized()  # Open the main window in maximized mode (taskbar visible)
    splash_widget.deleteLater()  # Clean up splash widget resources

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('logo-color.ico'))

    show_splash_screen(app)  # Launch splash screen

    exit_code = app.exec_()  # Run the application event loop
    print(f"Application exited with code: {exit_code}")

if __name__ == '__main__':
    main()
