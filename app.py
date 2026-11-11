import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtGui import QIcon, QPixmap

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)

    ui_path = resource_path(os.path.join("UI", "main.ui"))
    ui_file = QFile(ui_path)

    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Can not open this file: {ui_path}")
        sys.exit(-1)

    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()

    if not window:
        print(loader.errorString())
        sys.exit(-1)
    logo_path = resource_path(os.path.join("UI", "ICO.png"))
    window.setWindowIcon(QIcon(logo_path))
    bosch_logo_path = resource_path(os.path.join("UI", "Bosch-Logo.png"))
    label_logo = window.findChild(object, "label_logo")
    if label_logo:
        label_logo.setPixmap(QPixmap(bosch_logo_path))
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()