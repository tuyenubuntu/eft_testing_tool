# ui/general_ui.py
import sys
import os
import platform
import threading
import atexit
import signal
from typing import Optional, Set
from PySide6.QtWidgets import QApplication,QTabWidget, QPushButton, QTabWidget, QPlainTextEdit,QWidget, QTableView, QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit, QLabel, QMessageBox, QPlainTextEdit, QLineEdit, QDialog, QVBoxLayout, QComboBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QFileSystemWatcher, QObject, Signal,QTimer, QIODevice
from PySide6.QtGui import QIcon, QTextCursor
from ui.create_test_ui import CreateTestUI
from ui.load_test_ui import LoadTestUI
from ui.testing_ui import TestingUI
from ui.data_ui import DataUI
from services.config_reader import ConfigReader
from services.log_services import LogServices

class GeneralUI(QApplication):
    def __init__(self, ui_path="ui/general.ui", icon_path="ui/ICO.png", window_title="EFT-TESTING TOOL"):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.loader = QUiLoader()
        self.window = self.load_ui(ui_path)
        self.bind_widgets()
        # self.window.setWindowFlags(Qt.FramelessWindowHint)
        self.window.setWindowTitle(window_title)
        self.create_test_ui = CreateTestUI(self.window, self)
        self.load_test_ui = LoadTestUI(self.window, self)
        self.testing_ui = TestingUI(self.window, self)
        self.data_ui = DataUI(self.window, self)
        self.log_services = LogServices(save_to_file=True)
        
          # Bind widgets after the UI is loaded
        
        if icon_path and os.path.exists(icon_path):
            self.set_window_icon(icon_path)
        
        if window_title:
            self.set_window_title(window_title)
        
        if self.information_log and hasattr(self.information_log, "setReadOnly"):
            self.information_log.setReadOnly
    
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
        self.information_log = self.window.findChild(QPlainTextEdit, "information_log")
        self.progress_bar = self.window.findChild(QProgressBar, "progress_bar")
        self.tab_widget = self.window.findChild(QTabWidget, "tabWidget")
        self.information_test = self.window.findChild(QPlainTextEdit, "information_test")
        
        # Binding widgets to class attributes | Load test tab
        
        self.load_eft_machine = self.window.findChild(QLineEdit, "load_eft_machine")
        self.load_test_order_no = self.window.findChild(QLineEdit, "load_test_order_no")
        self.load_charge_no = self.window.findChild(QLineEdit, "load_charge_no")   
        self.load_task_name = self.window.findChild(QLineEdit, "load_task_name")
        self.load_element_type = self.window.findChild(QLineEdit, "load_element_type")
        self.load_line = self.window.findChild(QLineEdit, "load_line")
        self.load_process = self.window.findChild(QLineEdit, "load_process")
        self.load_axis = self.window.findChild(QLineEdit, "load_axis")
        self.load_requester = self.window.findChild(QLineEdit, "load_requester")
        self.load_quantity = self.window.findChild(QLineEdit, "load_quantity")
        self.load_sample_date = self.window.findChild(QLineEdit, "load_sample_date")
        self.load_remark = self.window.findChild(QPlainTextEdit, "load_remark")
        self.load_test_file = self.window.findChild(QLineEdit, "load_test_file")
        self.browse_btn = self.window.findChild(QPushButton, "browse_btn")
        self.start_test_btn_2 = self.window.findChild(QPushButton, "start_test_btn_2")
        self.monitor_btn = self.window.findChild(QPushButton, "monitor_btn")
        
        # Binding widgets to class attributes | Testing tab
        
        self.element_no = self.window.findChild(QLineEdit, "element_no")
        self.force_setting = self.window.findChild(QLineEdit, "force_setting")
        self.cycles = self.window.findChild(QLineEdit, "cycles")
        self.result = self.window.findChild(QLineEdit, "result")
        self.failure = self.window.findChild(QComboBox, "failure")
        self.input_person = self.window.findChild(QComboBox, "input_person")
        self.input_test_remark = self.window.findChild(QPlainTextEdit, "input_remark_testing")
        self.submit_btn = self.window.findChild(QPushButton, "submit_btn")
        self.close_btn = self.window.findChild(QPushButton, "close_btn")
        self.finish_btn = self.window.findChild(QPushButton, "finish_btn")
        self.table_results = self.window.findChild(QTableView, "table_results")
        
        # Binding widgets to class attributes | Data tab
        
        self.table_results_2 = self.window.findChild(QTableView, "table_results_2")
        self.close_btn_2 = self.window.findChild(QPushButton, "close_btn_2")
        self.finish_btn_2 = self.window.findChild(QPushButton, "finish_btn_2")

        # self.label = self.window.findChild(QLabel, "myLabel")
        # Add more widget bindings as needed
        
        if self.information_test:
            self.information_test.setReadOnly(True)
            
    def load_ui(self, ui_file_path):
        ui_file = QFile(ui_file_path)
        ui_file.open(QIODevice.ReadOnly)
        ui = self.loader.load(ui_file)
        ui_file.close()
        return ui
        
        return self.window
    
    def update_test_information(self, test_data):
        """Định dạng và hiển thị thông tin lô test lên khung Test Information bên phải"""
        if not getattr(self, "information_test", None):
            return

        if not test_data or "test_info" not in test_data:
            self.information_test.clear()
            return

        info = test_data.get("test_info", {})
        elements = test_data.get("elements", [])
        completed_count = sum(1 for el in elements if el.get("result"))
        total_count = info.get("quantity", len(elements))

        # Format
        summary_text = (
            f"EFT Machine: {info.get('eft_machine', '')}\n"
            f"Test Order No.: {info.get('test_order_no', '')}\n"
            f"Charge No.: {info.get('charge_no', '')}\n"
            f"Task Name: {info.get('task_name', '')}\n"
            f"Element Type: {info.get('element_type', '')}\n"
            f"Initial Force: {info.get('first_force_setting_n', '')} N\n"
            f"Line: {info.get('line', '')}\n"
            f"Process: {info.get('process', '')}\n"
            f"Axis: {info.get('axis', '')}\n"
            f"Requester: {info.get('requester_by', '')}\n"
            f"Sample Date: {info.get('sample_date', '')}\n"
            f"Progress: {completed_count} / {total_count}\n"
            f"Status: {info.get('status', '')}\n"
            f"Remark: {info.get('remark', '')}"
        )

        # Suport for all QTextEdit, QPlainTextEdit, QLabel
        if hasattr(self.information_test, "setPlainText"):
            self.information_test.setPlainText(summary_text)

        elif hasattr(self.information_test, "setText"):
            self.information_test.setText(summary_text)
        self.update_info_log(f"Loaded test information", level="INFO")

    def update_info_log(self, message, level="INFO"):
        """
        Ghi log mới vào khung Information ở dưới cùng giao diện[cite: 20].
        :param message: Nội dung thông báo
        :param level: 'INFO', 'SUCCESS', 'WARNING', hoặc 'ERROR'
        """
        plain_text, html_text = self.log_services.format_log(message, level)

        if not getattr(self, "information_log", None):
            print(plain_text)
            return

        # Support
        if hasattr(self.information_log, "appendHtml"):
            # QPlainTextEdit
            self.information_log.appendHtml(html_text)
        elif hasattr(self.information_log, "append"):
            # QTextEdit
            self.information_log.append(html_text)

        # Auto roll ResourceWarning
        self.information_log.moveCursor(QTextCursor.End)
    
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
        self.update_info_log(f"Start: EFT Creating Tool", level="INFO")
        self.window.show()
        sys.exit(self.app.exec())