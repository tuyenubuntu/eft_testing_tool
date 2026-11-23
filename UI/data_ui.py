import threading
import os
import numpy as np
from datetime import datetime
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap, QImage, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QComboBox, QTextEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QApplication, QWidget, QFileDialog, QMessageBox
from PySide6.QtWidgets import QComboBox, QTextEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QApplication, QWidget, QFileDialog, QMessageBox

from services.config_reader import ConfigReader
from services.test_file_manager import TestFileManager


class DataUI:
    def __init__(self, window: QWidget, generalUI):
        self.window = window
        self.config_reader = ConfigReader()
        self.TestFileManager = TestFileManager()
        self.test_data = None
        self.json_path = None
        self.generalUI = generalUI
        # self.generalUI.bind_widgets()  # Bind widgets after the UI is loaded
        self.widget_init()  # Initialize widgets with configuration data
        
        self.default_cycle = self.config_reader.get_default_cycle()
        self.adjust_force = self.config_reader.get_adjust_force()

    def widget_init(self):
        """
        Initialize the widgets in the "Testing" tab with data from configuration files.
        """
        # Example: Connect buttons to their respective handlers
        # You can add more widget initializations and event connections here as needed.

        # Initialize Model for QTableView
        self.table_model = QStandardItemModel()
        self.headers = ["Element No.", "Setting (N)", "Cycles (rpm)", "Result", "Failure", "Input Person", "Remark"]
        self.table_model.setHorizontalHeaderLabels(self.headers)
        if self.generalUI.table_results_2:
            self.generalUI.table_results_2.setModel(self.table_model)

        # 2. Connect signals to slots for user interactions
        if self.generalUI.finish_btn:
            self.generalUI.finish_btn.clicked.connect(self.handle_finish)
        if self.generalUI.close_btn_2:
            self.generalUI.close_btn_2.clicked.connect(self.handle_close)

    def start_session(self, json_path, test_data):
        """Function to start a testing session with the provided JSON path and test data."""
        self.json_path = json_path
        self.test_data = test_data

        # transfer test_info to the left panel
        if self.generalUI.tab_widget:
            self.generalUI.tab_widget.setCurrentIndex(3)

        # Disable the submit button until a valid element is loaded
        self.refresh_table()

        # find the first element that has no result yet and load it into the form
        elements = self.test_data.get("elements", [])
        next_idx = next((i for i, el in enumerate(elements) if not el.get("result")), None)
        if next_idx is not None:
            self.load_element_to_form(next_idx)


    def refresh_table(self):
        """Đổ dữ liệu từ self.test_data['elements'] lên QTableView"""
        self.table_model.setRowCount(0)
        for el in self.test_data.get("elements", []):
            row = [
                QStandardItem(str(el.get("element_no", ""))),
                QStandardItem(str(el.get("setting_N", ""))),
                QStandardItem(str(el.get("cycles_rpm", ""))),
                QStandardItem(str(el.get("result", ""))),
                QStandardItem(str(el.get("failure", ""))),
                QStandardItem(str(el.get("input_person", ""))),
                QStandardItem(str(el.get("input_remark_testing", ""))),
            ]
            self.table_model.appendRow(row)

    def load_element_to_form(self, index):
            """Load the data of the element at the given index into the form for testing."""
            self.current_index = index
            elements = self.test_data.get("elements", [])
            test_info = self.test_data.get("test_info", {})
            current_el = elements[index]

            self.generalUI.element_no.setText(str(current_el.get("element_no", index + 1)))

    def handle_finish(self):
        """Mark the test batch as finished and save the file"""
        if not self.test_data or not self.json_path:
            return

        # Check if all elements have been tested
        unfinished = [el["element_no"] for el in self.test_data["elements"] if not el.get("result")]
        if unfinished:
            reply = QMessageBox.question(
                self.window,
                "Not all elements tested",
                f"There are still elements without results: {unfinished}.\nDo you still want to mark as Finished?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        self.test_data["test_info"]["status"] = "Finished"
        TestFileManager.save_test_json(self.json_path, self.test_data)
        QMessageBox.information(self.window, "Completed", "Test batch marked as finished!")

    def reset_testing_ui(self):
        """Clear all input fields and reset the TestingUI state for a new session."""
        # 1. Reset internal state variables
        self.json_path = None
        self.test_data = None
        self.current_index = 0

        if hasattr(self.generalUI, "current_json_path"):
            self.generalUI.current_json_path = None
        if hasattr(self.generalUI, "current_test_data"):
            self.generalUI.current_test_data = None

        # 2. Clear all input fields in the Testing tab


        # 3. Clear all rows in the Result table
        if hasattr(self, "table_model") and self.table_model:
            self.table_model.setRowCount(0)

        if self.generalUI.information_test:
            self.generalUI.information_test.clear()

    def handle_close(self):
        """Close the current test session: clear data on the UI and return to the Create tab, without closing the app"""
        reply = QMessageBox.question(
            self.window,
            "Confirm Close",
            "All submitted results have been automatically saved.\nDo you want to close this test session?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reset_testing_ui()

            # Optional: Log the closure of the test session in the information log if it exists
            if hasattr(self.generalUI, "textEdit_Information") and self.generalUI.textEdit_Information:
                self.generalUI.textEdit_Information.append("[INFO] Closed current test session.")

            # Switch the screen back to the Create tab (index 0) or Load test tab (index 1)
            if self.generalUI.tab_widget:
                self.generalUI.tab_widget.setCurrentIndex(0)