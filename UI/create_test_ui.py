import threading
import os
import numpy as np
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QTimer, QIODevice
from PySide6.QtGui import QPixmap, QImage, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QComboBox, QTextEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QApplication, QWidget, QFileDialog, QMessageBox
from PySide6.QtWidgets import QComboBox, QTextEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QApplication, QWidget, QFileDialog, QMessageBox

from services.config_reader import ConfigReader
from services.test_file_manager import TestFileManager


class CreateTestUI:
    def __init__(self, window: QWidget, generalUI):
        self.window = window
        self.config_reader = ConfigReader()
        self.test_file_manager = TestFileManager()
        self.generalUI = generalUI
        
        # self.generalUI.bind_widgets()  # Bind widgets after the UI is loaded
        self.widget_init()             # Initialize widgets with configuration data

    def widget_init(self):
        """
        Khởi tạo các ComboBox với dữ liệu từ file cấu hình và kết nối sự kiện nút bấm. 
        """
        configs = self.config_reader.get_general_configs()

        # Initialize ComboBoxes in the "Create" tab
        self.generalUI.input_eft_machine.clear()
        self.generalUI.input_task_name.clear()
        self.generalUI.input_element_type.clear()
        self.generalUI.input_line.clear()
        self.generalUI.input_process.clear()
        self.generalUI.input_axis.clear()
        self.generalUI.input_requester.clear()

        self.generalUI.input_eft_machine.addItems(configs["eft_machines"])
        self.generalUI.input_task_name.addItems(configs["task_names"])
        self.generalUI.input_element_type.addItems(configs["element_types"])
        self.generalUI.input_line.addItems(configs["lines"])
        self.generalUI.input_process.addItems(configs["processes"])
        self.generalUI.input_axis.addItems(configs["axes"])
        self.generalUI.input_requester.addItems(configs["requested_by"])

        # Connect button event
        self.generalUI.create_btn.clicked.connect(self.handle_create_file)
        self.generalUI.start_test_btn_1.clicked.connect(self.handle_start_testing)

    def build_and_save_json(self):
        """
        Thu thập dữ liệu trên tab Create, mở hộp thoại lưu file JSON và trả về (save_path, test_data).
        """
        path = self.config_reader.get_path_configs()

        # 1. Collect 
        test_order_no = self.generalUI.input_test_order_no.text().strip()
        quantity_text = self.generalUI.input_quantity.text().strip()

        if not test_order_no:
            QMessageBox.warning(self.window, "Missing Information", "Please enter the Test Order No.!")
            self.generalUI.update_info_log(f"Missing Information:" "Please enter the Test Order No.!", level="WARNING")
            return None, None

        if not quantity_text.isdigit() or int(quantity_text) <= 0:
            QMessageBox.warning(self.window, "Invalid Format", "Quantity must be an integer greater than 0!")
            self.generalUI.update_info_log(f"Invalid Format:" "Quantity must be an integer greater than 0!", level="WARNING")
            return None, None

        element_type = self.generalUI.input_element_type.currentText()

        info_data = {
            "eft_machine": self.generalUI.input_eft_machine.currentText(),
            "test_order_no": test_order_no,
            "charge_no": self.generalUI.input_charge_no.text().strip(),
            "task_name": self.generalUI.input_task_name.currentText(),
            "element_type": element_type,
            "line": self.generalUI.input_line.currentText(),
            "process": self.generalUI.input_process.currentText(),
            "axis": self.generalUI.input_axis.currentText(),
            "requester_by": self.generalUI.input_requester.currentText(),
            "quantity": int(quantity_text),
            "sample_date": self.generalUI.input_sample_date.text().strip(),
            "remark": self.generalUI.input_remark.toPlainText().strip()
        }

        # 2. add default force setting based on element type
        default_force = self.config_reader.get_force_by_element(element_type) or ""

        # 3. Open a file dialog to select the save path for the JSON file
        default_dir = path.get("TestFiles", "")
        if default_dir:
            os.makedirs(default_dir, exist_ok=True)
            
        default_filename = f"{test_order_no}_{element_type}.json"
        save_path, _ = QFileDialog.getSaveFileName(
            self.window,
            "Lưu file test",
            os.path.join(default_dir, default_filename),
            "JSON Files (*.json)"
        )

        if not save_path:
            return None, None  # Push cancel button

        # 4. record
        try:
            self.test_file_manager.create_test_json(save_path, info_data, default_setting_n=default_force)
            test_data = self.test_file_manager.load_test_json(save_path)

            # Save path
            self.generalUI.current_json_path = save_path
            self.generalUI.current_test_data = test_data

            if hasattr(self.generalUI, "textEdit_Information"):
                self.generalUI.textEdit_Information.append(f"[OK] Created file successfully: {save_path}")

            return save_path, test_data

        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Failed to create file:\n{str(e)}")
            self.generalUI.update_info_log(f"Failed to create file: {save_path}", level="ERROR")
            return None, None

    def handle_create_file(self):
        """
        Only create file and save json file, hold on tab Create.
        """
        save_path, _ = self.build_and_save_json()
        if save_path:
            QMessageBox.information(self.window, "Success", f"Created file successfully:\n{save_path}")
            self.generalUI.update_info_log(f"Created test file: {save_path}", level="SUCCESS")

    def handle_start_testing(self):
        """
        Lưu file JSON, sau đó tự động chuyển thẳng sang tab Testing và nạp sẵn dữ liệu để test.
        """
        save_path, test_data = self.build_and_save_json()
        if not save_path or not test_data:
            return

        if not test_data.get("elements"):
            QMessageBox.warning(self.window, "No Samples Found", "The test file does not contain any samples to be tested!")
            self.generalUI.update_info_log(f"No Samples Found: {save_path}", level="WARNING")
            return

        # Update result table 
        if hasattr(self.generalUI, "refresh_table"):
            self.generalUI.testing_ui.refresh_table()  # Cập nhật bảng kết quả với dữ liệu mới

        # Chuyển sang tab Testing (index 2) và nạp mẫu đầu tiên lên form
        self.generalUI.tab_widget.setCurrentIndex(2)
        self.generalUI.testing_ui.start_session(save_path, test_data)
        self.generalUI.testing_ui.load_element_to_form(0)
        
        self.generalUI.update_test_information(test_data)
        self.generalUI.update_info_log(f"Created and started test: {save_path}", level="INFO")
