from qt import QtWidgets, QtGui, QtCore, Qt
#!/usr/bin/env python3
"""
Setup script to configure the AI Capture application with default paths and settings.
Run this once before using the application.
"""

import os
import sys

def setup_application():
    """Configure the application with default settings."""
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "dataset")
    labels_path = os.path.join(current_dir, "labels.txt")
    
    print(f"Setting up AI Capture application...")
    print(f"Dataset path: {dataset_path}")
    print(f"Labels path: {labels_path}")
    
    # Create QApplication (required for QSettings)
    app = QtWidgets.QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    
    # Configure settings for the detector component
    settings = QtCore.QSettings("AICapture", "MainApp")
    
    # Set detector settings
    settings.beginGroup("detector")
    settings.setValue("dataset_path", dataset_path)
    settings.setValue("class_labels_path", labels_path)
    settings.setValue("jpeg_quality", 95)
    settings.endGroup()
    
    # Set general settings
    settings.beginGroup("General")
    settings.setValue("dataset_path", dataset_path)
    settings.setValue("class_labels_path", labels_path)
    settings.endGroup()
    
    settings.sync()
    
    print("✅ Settings configured successfully!")
    print("\nYou can now run the application with:")
    print("python main.py 0  # for camera 0")
    print("python main.py 1  # for camera 1")
    print("\nThe freeze functionality should now work properly.")
    
    return True

if __name__ == "__main__":
    setup_application()
