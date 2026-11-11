import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtGui import QIcon

class MainApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.main_window = None

    def load_ui(self, ui_file_path):
        ui_file = QFile(ui_file_path)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open UI file: {ui_file_path}")
            sys.exit(-1)

        loader = QUiLoader()
        self.main_window = loader.load(ui_file)
        ui_file.close()

        if not self.main_window:
            print(loader.errorString())
            sys.exit(-1)

        return self.main_window
    
    def bind_widgets(self):
        if not self.main_window:
            print("Main window is not loaded.")
            sys.exit(-1)
        
        # Example of binding widgets to class attributes
        self.create_btn = self.main_window.findChild(QPushButton, "create_btn")
        self.input_eft_machine = self.main_window.findChild(QComboBox, "input_eft_machine")
        self.input_test_order_no = self.main_window.findChild(QLineEdit, "input_test_order_no")
        self.input_charge_no = self.main_window.findChild(QLineEdit, "input_charge_no")
        self.input_task_name = self.main_window.findChild(QComboBox, "input_task_name")
        self.input_element_type = self.main_window.findChild(QComboBox, "input_element_type")
        self.input_line = self.main_window.findChild(QComboBox, "input_line")
        self.input_process = self.main_window.findChild(QComboBox, "input_process")
        self.input_axis = self.main_window.findChild(QComboBox, "input_axis")
        self.input_requester = self.main_window.findChild(QComboBox, "input_requester")
        self.input_quantity = self.main_window.findChild(QLineEdit, "input_quantity")
        self.input_sample_date = self.main_window.findChild(QLineEdit, "input_sample_date")
        self.input_remark = self.main_window.findChild(QPlainTextEdit, "input_remark")
        self.information_text = self.main_window.findChild(QTextEdit, "information_text")
        self.progress_bar = self.main_window.findChild(QProgressBar, "progress_bar")
        
        # self.label = self.main_window.findChild(QLabel, "myLabel")
        # Add more widget bindings as needed
        
    
    def set_window_icon(self, icon_path):
        icon = QIcon(icon_path)
        if self.main_window:
            self.main_window.setWindowIcon(icon)
            
    def show_main_window(self):
        if self.main_window:
            self.main_window.show()
        else:
            print("Main window is not loaded.")
            sys.exit(-1)
    
    def exec_app(self):
        sys.exit(self.exec())   

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
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()