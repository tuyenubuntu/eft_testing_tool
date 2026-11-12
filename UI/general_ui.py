# ui/general_ui.py
import sys
import os
import platform
import threading
import atexit
import signal
from typing import Optional, Set
from PySide6.QtWidgets import QApplication, QPushButton, QTabWidget, QWidget, QTableView, QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit, QLabel, QMessageBox, QPlainTextEdit, QLineEdit, QDialog, QVBoxLayout, QComboBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QFileSystemWatcher, QObject, Signal,QTimer, QIODevice
from PySide6.QtGui import QIcon
from ui.main_ui import MainUI

class GeneralUI(QApplication):
    def __init__(self, ui_path="ui/main.ui", icon_path="ui/ICO.png", window_title="EFT-TESTING TOOL"):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.loader = QUiLoader()
        self.window = self.load_ui(ui_path)
        # self.window.setWindowFlags(Qt.FramelessWindowHint)
        self.window.setWindowTitle(window_title)
        self.main_window = MainUI(self.window, self)
        
        self.bind_widgets()  # Bind widgets after the UI is loaded
        
        if icon_path and os.path.exists(icon_path):
            self.set_window_icon(icon_path)
        
        if window_title:
            self.set_window_title(window_title)
    
    def bind_widgets(self):
        
        # Binding widgets to class attributes | Create tab
        self.create_btn = self.window.findChild(QPushButton, "create_btn")
        self.input_eft_machine = self.window.findChild(QComboBox, "input_eft_machine")
        self.input_test_order_no = self.window.findChild(QLineEdit, "input_test_order_no")
        self.input_charge_no = self.window.findChild(QLineEdit, "input_charge_no")
        self.input_task_name = self.window.findChild(QComboBox, "input_task_name")
        self.input_element_type = self.window.findChild(QComboBox, "input_element_type")
        self.input_line = self.window.findChild(QComboBox, "input_line")
        self.input_process = self.window.findChild(QComboBox, "input_process")
        self.input_axis = self.window.findChild(QComboBox, "input_axis")
        self.input_requester = self.window.findChild(QComboBox, "input_requester")
        self.input_quantity = self.window.findChild(QLineEdit, "input_quantity")
        self.input_sample_date = self.window.findChild(QLineEdit, "input_sample_date")
        self.input_remark = self.window.findChild(QPlainTextEdit, "input_remark")
        self.start_test_btn_1 = self.window.findChild(QPushButton, "start_test_btn_1")
        self.information_log = self.window.findChild(QTextEdit, "information_log")
        self.progress_bar = self.window.findChild(QProgressBar, "progress_bar")
        
        # Binding widgets to class attributes | Load test tab
        
        self.load_eft_machine = self.window.findChild(QComboBox, "load_eft_machine")
        self.load_test_order_no = self.window.findChild(QComboBox, "load_test_order_no")
        self.load_charge_no = self.window.findChild(QComboBox, "load_charge_no")   
        self.load_task_name = self.window.findChild(QComboBox, "load_task_name")
        self.load_element_type = self.window.findChild(QComboBox, "load_element_type")
        self.load_line = self.window.findChild(QComboBox, "load_line")
        self.load_process = self.window.findChild(QComboBox, "load_process")
        self.load_axis = self.window.findChild(QComboBox, "load_axis")
        self.load_requester = self.window.findChild(QComboBox, "load_requester")
        self.load_quantity = self.window.findChild(QLineEdit, "load_quantity")
        self.load_sample_date = self.window.findChild(QLineEdit, "load_sample_date")
        self.load_remark = self.window.findChild(QPlainTextEdit, "load_remark")
        self.load_test_file = self.window.findChild(QLineEdit, "load_test_file")
        self.browse_btn = self.window.findChild(QPushButton, "browse_btn")
        self.start_test_btn_2 = self.window.findChild(QPushButton, "start_test_btn_2")
        
        # Binding widgets to class attributes | Testing tab
        
        self.element_no = self.window.findChild(QLineEdit, "element_no")
        self.force_setting = self.window.findChild(QLineEdit, "force_setting")
        self.cycles = self.window.findChild(QLineEdit, "cycles")
        self.result = self.window.findChild(QLineEdit, "result")
        self.failure = self.window.findChild(QComboBox, "failure")
        self.input_person = self.window.findChild(QComboBox, "input_person")
        self.test_remark = self.window.findChild(QPlainTextEdit, "test_remark")
        self.submit_btn = self.window.findChild(QPushButton, "submit_btn")
        self.close_btn = self.window.findChild(QPushButton, "close_btn")
        self.finish_btn = self.window.findChild(QPushButton, "finish_btn")
        self.table_results = self.window.findChild(QTableView, "table_results")
        
        # Binding widgets to class attributes | Data tab
        
        self.input_test_order_no_2 = self.window.findChild(QLineEdit, "input_test_order_no_2")
        self.input_charge_no_2 = self.window.findChild(QLineEdit, "input_charge_no_2")
        self.search_btn = self.window.findChild(QPushButton, "search_btn")

        # self.label = self.window.findChild(QLabel, "myLabel")
        # Add more widget bindings as needed
    
    def load_ui(self, ui_file_path):
        ui_file = QFile(ui_file_path)
        ui_file.open(QIODevice.ReadOnly)
        ui = self.loader.load(ui_file)
        ui_file.close()
        return ui
        
        return self.window
    
    def set_window_icon(self, icon_path):
        if not os.path.exists(icon_path):
            print(f"Icon file does not exist: {icon_path}")
            return
        icon = QIcon(icon_path)
        self.app.setWindowIcon(icon)
        self.window.setWindowIcon(icon)
    
    def set_window_title(self, title):
        self.window.setWindowTitle(title)
        
            
    def show_main_window(self):
        if self.window:
            self.window.show()
        else:
            print("Main window is not loaded.")
            sys.exit(-1)
    
    def run(self):
        self.window.show()
        sys.exit(self.app.exec())