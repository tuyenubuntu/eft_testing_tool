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
from services.result_reader import ResultReader


class TestingUI:
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
        if self.generalUI.element_no:
            self.generalUI.element_no.setReadOnly(True)
        if self.generalUI.result:
            self.generalUI.result.setReadOnly(True)
        if self.generalUI.force_setting:
            self.generalUI.force_setting.setReadOnly(True)

        # Initialize Model for QTableView
        self.table_model = QStandardItemModel()
        self.headers = ["Element No.", "Setting (N)", "Cycles (rpm)", "Result", "Failure", "Input Person", "Remark"]
        self.table_model.setHorizontalHeaderLabels(self.headers)
        if self.generalUI.table_results:
            self.generalUI.table_results.setModel(self.table_model)

        # 2. Connect signals to slots for user interactions
        if self.generalUI.cycles:
            self.generalUI.cycles.textChanged.connect(self.on_cycles_changed)
        if self.generalUI.submit_btn:
            self.generalUI.submit_btn.clicked.connect(self.handle_submit)
        if self.generalUI.finish_btn:
            self.generalUI.finish_btn.clicked.connect(self.handle_finish)
        if self.generalUI.close_btn:
            self.generalUI.close_btn.clicked.connect(self.handle_close)
            
        if self.generalUI.load_path_result:
            self.generalUI.load_path_result.setReadOnly(True)
            self.generalUI.load_path_result.textChanged.connect(self.on_result_path_changed)

        if self.generalUI.browse_btn_2:
            self.generalUI.browse_btn_2.clicked.connect(self.handle_browse_result_folder)

        if self.generalUI.get_cycles_btn:
            self.generalUI.get_cycles_btn.setEnabled(False)  # Disabled until result folder is mapped
            self.generalUI.get_cycles_btn.clicked.connect(self.handle_get_cycles)

    def start_session(self, json_path, test_data):
        """Function to start a testing session with the provided JSON path and test data."""
        self.json_path = json_path
        self.test_data = test_data

        # transfer test_info to the left panel
        if self.generalUI.tab_widget:
            self.generalUI.tab_widget.setCurrentIndex(2)

        # Disable the submit button until a valid element is loaded
        self.refresh_table()
        self.generalUI.update_progress_bar(self.test_data)
        # print ("First refesh")

        # find the first element that has no result yet and load it into the form
        elements = self.test_data.get("elements", [])
        next_idx = next((i for i, el in enumerate(elements) if not el.get("result")), None)

        if next_idx is not None:
            self.load_element_to_form(next_idx)
        else:
            QMessageBox.information(self.window, "Information", "All elements have been tested!")
            self.generalUI.submit_btn.setEnabled(False)

    def refresh_table(self):
        """Collect data from self.test_data['elements'] lên QTableView"""
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

            # Calculate the force setting for the current element based on the previous element's result
            if index == 0:
                # For the first element, use the default force setting from test_info
                force_val = str(test_info.get("first_force_setting_n", "")).strip()
            else:
                # For subsequent elements, adjust the force based on the previous element's result
                prev_el = elements[index - 1]
                try:
                    prev_force = int(float(prev_el.get("setting_N", 0)))
                    if prev_el.get("result") == "Not break":
                        force_val = str(prev_force + int(self.adjust_force))
                    else:
                        force_val = str(max(int(self.adjust_force), prev_force - int(self.adjust_force)))  # Ensure it doesn't go below the adjust force
                except ValueError:
                    force_val = ""

            # Display the calculated force setting in the form
            self.generalUI.force_setting.setText(force_val)

            # reset other fields for the current element
            self.generalUI.cycles.clear()
            self.generalUI.result.clear()
            self.generalUI.failure.setCurrentIndex(-1)
            self.generalUI.failure.setEnabled(True)
            if self.generalUI.input_test_remark:
                self.generalUI.input_test_remark.clear()
            self.generalUI.submit_btn.setEnabled(True)
            self.generalUI.cycles.setFocus()
            
    def on_cycles_changed(self, text):
        """Automatically determine the result based on the cycles input and update the Failure field accordingly."""
        clean_text = text.strip().replace(",", "")
        if not clean_text.isdigit():
            self.generalUI.result.clear()
            return

        cycles_val = int(clean_text)
        if cycles_val >= int(self.default_cycle):
            self.generalUI.result.setText("Not break")
            # if the result is "Not break", reset the Failure field to its default state
            self.generalUI.failure.setCurrentIndex(-1)
            self.generalUI.failure.setCurrentText("")
            self.generalUI.failure.setEnabled(False)
        else:
            self.generalUI.result.setText("Break")
            # if the result is "Break", enable the Failure field for user selection
            self.generalUI.failure.setEnabled(True)
            if self.generalUI.failure.currentIndex() == -1 and self.generalUI.failure.count() > 0:
                self.generalUI.failure.setCurrentIndex(0)

    def handle_submit(self):
            """Save the results of the current element before moving to the next one"""
            if not self.test_data or not self.json_path:
                return

            cycles_str = self.generalUI.cycles.text().strip()
            result_str = self.generalUI.result.text().strip() 
            current_force_str = self.generalUI.force_setting.text().strip()

            if not cycles_str or not result_str:
                QMessageBox.warning(self.window, "Missing Data", "Please enter a valid Cycles (rpm) value!")
                return

            if result_str == "Break" and not self.generalUI.failure.currentText().strip():
                QMessageBox.warning(self.window, "Missing Data", "Element is broken, please select a Failure reason/position!")
                return

            

            # Step 1: Update the current element's data in self.test_data
            el = self.test_data["elements"][self.current_index]
            el["setting_N"] = current_force_str
            el["cycles_rpm"] = cycles_str
            el["result"] = result_str
            el["failure"] = "" if result_str == "Not break" else self.generalUI.failure.currentText().strip()
            el["input_person"] = self.generalUI.input_person.currentText().strip()
            el["remark"] = self.generalUI.input_test_remark.toPlainText().strip() if self.generalUI.input_test_remark else ""

            # Step 2: Save the updated test data back to the JSON file
            TestFileManager.save_test_json(self.json_path, self.test_data)
            self.refresh_table()
            self.generalUI.update_test_information(self.test_data)
            self.generalUI.update_progress_bar(self.test_data)
            # print("Test1")

            # Step 3: Move to the next element for testing
            next_index = self.current_index + 1
            if next_index < len(self.test_data["elements"]):
                self.load_element_to_form(next_index)
            else:
                self.generalUI.submit_btn.setEnabled(False)
                QMessageBox.information(
                    self.window,
                    "Completed",
                    "All elements have been tested! Please click 'Finished' to complete the test batch."
                )
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
        self.test_data["test_info"]["finished_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        TestFileManager.save_test_json(self.json_path, self.test_data)
        QMessageBox.information(self.window, "Completed", "Test batch marked as finished!")
        self.reset_testing_ui()
        self.generalUI.update_progress_bar(None)
        
        # Optional: Log the closure of the test session in the information log if it exists
        if hasattr(self.generalUI, "textEdit_Information") and self.generalUI.textEdit_Information:
            self.generalUI.textEdit_Information.append("[INFO] Closed current test session.")

        # # Switch the screen back to the Create tab (index 0) or Load test tab (index 1)
        # if self.generalUI.tab_widget:
        #     self.generalUI.tab_widget.setCurrentIndex(0)
        self.generalUI.update_info_log(f"Finished: {self.generalUI.info.get('test_order_no', '')}")


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
        if self.generalUI.element_no:
            self.generalUI.element_no.clear()
        if self.generalUI.force_setting:
            self.generalUI.force_setting.clear()
        if self.generalUI.cycles:
            self.generalUI.cycles.clear()
        if self.generalUI.result:
            self.generalUI.result.clear()
        if self.generalUI.failure:
            self.generalUI.failure.setCurrentIndex(-1)
            self.generalUI.failure.setEnabled(True)
        if self.generalUI.input_test_remark:
            self.generalUI.input_test_remark.clear()

        # 3. Clear all rows in the Result table
        if hasattr(self, "table_model") and self.table_model:
            self.table_model.setRowCount(0)

        # 4. Enable the Submit button for the next session
        if self.generalUI.submit_btn:
            self.generalUI.submit_btn.setEnabled(True)

        if self.generalUI.information_test:
            self.generalUI.information_test.clear()
            
        if self.generalUI.load_path_result:
            self.generalUI.load_path_result.clear()
        if self.generalUI.get_cycles_btn:
            self.generalUI.get_cycles_btn.setEnabled(False)

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
            self.generalUI.update_progress_bar(None)

            # Optional: Log the closure of the test session in the information log if it exists
            if hasattr(self.generalUI, "textEdit_Information") and self.generalUI.textEdit_Information:
                self.generalUI.textEdit_Information.append("[INFO] Closed current test session.")

            # # Switch the screen back to the Create tab (index 0) or Load test tab (index 1)
            # if self.generalUI.tab_widget:
            #     self.generalUI.tab_widget.setCurrentIndex(0)
    
    def on_result_path_changed(self, text: str):
        """Enable 'Get cycles' button only when a valid result folder path is mapped."""
        has_valid_folder = bool(text.strip()) and os.path.isdir(text.strip())
        if self.generalUI.get_cycles_btn:
            self.generalUI.get_cycles_btn.setEnabled(has_valid_folder)

    def handle_browse_result_folder(self):
        """Open dialog to select the machine result folder and validate Charge No. match."""
        if not self.test_data:
            QMessageBox.warning(self.window, "No Active Test", "Please create or load a test order first!")
            return

        folder_path = QFileDialog.getExistingDirectory(
            self.window,
            "Select Machine Result Folder",
            ""
        )
        if not folder_path:
            return

        expected_charge_no = self.test_data.get("test_info", {}).get("charge_no", "")
        is_valid, err_msg = ResultReader.validate_result_folder(folder_path, expected_charge_no)

        if not is_valid:
            QMessageBox.critical(self.window, "Wrong Result Folder", err_msg)
            if self.generalUI.load_path_result:
                self.generalUI.load_path_result.clear()
            if hasattr(self.generalUI, "update_info_log"):
                self.generalUI.update_info_log(
                    f"Rejected result folder '{os.path.basename(folder_path)}' (Expected Charge No.: {expected_charge_no})",
                    level="ERROR"
                )
            return

        if self.generalUI.load_path_result:
            self.generalUI.load_path_result.setText(folder_path)
        if hasattr(self.generalUI, "update_info_log"):
            self.generalUI.update_info_log(f"Mapped result folder: {folder_path}", level="INFO")

    def handle_get_cycles(self):
        """Fetch the final cycles for the current element after verifying Charge No. match."""
        if not self.test_data:
            return

        folder_path = self.generalUI.load_path_result.text().strip() if self.generalUI.load_path_result else ""
        expected_charge_no = self.test_data.get("test_info", {}).get("charge_no", "")

        is_valid, err_msg = ResultReader.validate_result_folder(folder_path, expected_charge_no)
        if not is_valid:
            QMessageBox.critical(self.window, "Wrong Result Folder", err_msg)
            return

        current_el = self.test_data["elements"][self.current_index]
        element_no = int(current_el.get("element_no", self.current_index + 1))

        try:
            cycles_val = ResultReader.get_cycles_from_folder(
                folder_path=folder_path,
                element_no=element_no,
                machine_type="TYPE_1"
            )
            self.generalUI.cycles.setText(cycles_val)

            if hasattr(self.generalUI, "update_info_log"):
                self.generalUI.update_info_log(
                    f"Fetched {cycles_val} cycles for Element #{element_no} from {element_no}.Woe",
                    level="SUCCESS"
                )

        except Exception as e:
            QMessageBox.warning(self.window, "Get Cycles Failed", str(e))
            if hasattr(self.generalUI, "update_info_log"):
                self.generalUI.update_info_log(f"Get cycles error (Element #{element_no}): {str(e)}", level="ERROR")