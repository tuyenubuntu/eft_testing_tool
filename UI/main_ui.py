import threading
import os
import numpy as np
from datetime import datetime
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QComboBox, QTextEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QApplication, QWidget

class MainUI:
    def __init__(self, window: QWidget, generalUI):
        self.window = window
        self.generalUI = generalUI
        self.generalUI.bind_widgets()  # Bind widgets after the UI is loaded