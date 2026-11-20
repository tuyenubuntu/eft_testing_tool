import threading
import os
import numpy as np
from datetime import datetime
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QComboBox, QTextEdit, QLineEdit, QPlainTextEdit , QPushButton, QLabel, QTableWidget, QTableWidgetItem, QApplication, QWidget, QFileDialog, QMessageBox

from services.config_reader import ConfigReader
from services.test_file_manager import TestFileManager

class LoadTestUI:
    def __init__(self, window: QWidget, generalUI):
        self.window = window
        self.config_reader = ConfigReader()
        self.TestFileManager = TestFileManager()
        self.generalUI = generalUI
        # self.generalUI.bind_widgets()  # Bind widgets after the UI is loaded
        self.widget_init()  # Initialize widgets with configuration data

    def widget_init(self):
        """
        Initialize the widgets in the "Load Test" tab with data from configuration files.
        """
        self.generalUI.browse_btn.clicked.connect(self.handle_load_test_file)
        self.generalUI.start_test_btn_2.clicked.connect(self.handle_start_loaded_test)
        self.generalUI.monitor_btn.clicked.connect(self.handle_monitor)
        

    def handle_load_test_file(self):
        # 1. collect the default directory for test files from configuration
        reader = ConfigReader()
        default_dir = reader.get_test_files_dir()

        # 2. Open a file dialog to select a JSON test file
        file_path, _ = QFileDialog.getOpenFileName(self.window, "Select Test JSON File", default_dir, "JSON Files (*.json)")

        if not file_path:
            return  # Path is empty, user canceled the dialog

        try:
            # 3. read the selected JSON file and store its content in self.current_test_data
            self.current_test_data = self.TestFileManager.load_test_json(file_path)
            self.current_json_path = file_path
            info = self.current_test_data.get("test_info", {})

            # 4. Set the file path in the QLineEdit for display
            self.load_test_file = self.window.findChild(QLineEdit, "load_test_file")
            self.load_test_file.setText(file_path)

            # 5. Populate the fields in the "Load Test" tab with the data from the JSON file
            self.generalUI.load_eft_machine.setText(str(info.get("eft_machine", "")))
            self.generalUI.load_test_order_no.setText(str(info.get("test_order_no", "")))
            self.generalUI.load_charge_no.setText(str(info.get("charge_no", "")))
            self.generalUI.load_task_name.setText(str(info.get("task_name", "")))
            self.generalUI.load_element_type.setText(str(info.get("element_type", "")))
            self.generalUI.load_line.setText(str(info.get("line", "")))
            self.generalUI.load_process.setText(str(info.get("process", "")))
            self.generalUI.load_axis.setText(str(info.get("axis", "")))
            self.generalUI.load_requester.setText(str(info.get("requester_by", "")))
            self.generalUI.load_quantity.setText(str(info.get("quantity", "")))
            self.generalUI.load_sample_date.setText(str(info.get("sample_date", "")))

            # Set the remark field in the QPlainTextEdit
            self.generalUI.load_remark = self.window.findChild(QPlainTextEdit, "load_remark")
            self.generalUI.load_remark.setPlainText(str(info.get("remark", "")))
            
            self.generalUI.update_test_information(self.current_test_data)

        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Cannot load data from JSON file:\n{str(e)}")

    def handle_start_loaded_test(self):
        if not getattr(self, "current_json_path", None) or not getattr(self, "current_test_data", None):
            QMessageBox.warning(self.window, "Not Selected", "Please select a Test JSON file before clicking Start Test!")
            return
        self.generalUI.testing_ui.start_session(self.current_json_path, self.current_test_data)
        
        self.generalUI.update_test_information(self.current_test_data)
        
    def handle_monitor(self):
        # Implement the logic for monitoring the test session
        if not getattr(self, "current_json_path", None) or not getattr(self, "current_test_data", None):
            QMessageBox.warning(self.window, "Not Selected", "Please select a Test JSON file before clicking Start Test!")
            return
        self.generalUI.data_ui.start_session(self.current_json_path, self.current_test_data)
        
        self.generalUI.update_test_information(self.current_test_data)