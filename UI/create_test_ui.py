import os
from datetime import datetime
from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PySide6.QtCore import QDate, Qt
from services.config_reader import ConfigReader
from services.test_file_manager import TestFileManager


class CreateTestUI:
    def __init__(self, window: QWidget, generalUI):
        self.window = window
        self.config_reader = ConfigReader()
        self.test_file_manager = TestFileManager()
        self.generalUI = generalUI

        self.widget_init()

    def widget_init(self):
        """
        Initialize ComboBoxes with configuration data and connect button signals.
        """
        configs = self.config_reader.get_general_configs()

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

        # Pre-fill current date for Sample Date if the field is empty
        if not self.generalUI.input_sample_date.text().strip():
            self.generalUI.input_sample_date.setText(datetime.now().strftime("%d/%m/%Y"))
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_day = datetime.now().day
        if self.generalUI.input_sample_date:
            self.generalUI.input_sample_date.setDisplayFormat("yyyy-MM-dd")
            self.generalUI.input_sample_date.setCalendarPopup(True)
            self.generalUI.input_sample_date.setDate(QDate.currentDate())

        self.generalUI.create_btn.clicked.connect(self.handle_create_file)
        self.generalUI.start_test_btn_1.clicked.connect(self.handle_start_testing)

    def _parse_sample_date(self, date_val):
        """
        Convert a QDate object (or fallback date string) and return (year_yyyy, yymmdd).
        """
        if isinstance(date_val, QDate):
            if not date_val.isValid():
                return None, None
            return date_val.toString("yyyy"), date_val.toString("yyMMdd")

        # Fallback if a string is passed
        if isinstance(date_val, str):
            formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%y", "%y%m%d"]
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_val.strip(), fmt)
                    return dt.strftime("%Y"), dt.strftime("%y%m%d")
                except ValueError:
                    continue

        return None, None

    def build_and_save_json(self):
        """
        Validate required fields, build year-based folder structure and standard filename,
        and save the JSON test file.
        """
        path_cfg = self.config_reader.get_path_configs()

        # 1. Collect UI inputs
        test_order_no = self.generalUI.input_test_order_no.text().strip()
        charge_no = self.generalUI.input_charge_no.text().strip()
        quantity_text = self.generalUI.input_quantity.text().strip()
        sample_date = self.generalUI.input_sample_date.text().strip()

        # 2. Validate REQUIRED fields: Charge No., Quantity, Sample Date
        if not charge_no:
            QMessageBox.warning(self.window, "Missing Information", "Please enter the Charge No.!")
            self.generalUI.update_info_log("Missing Information: Please enter the Charge No.!", level="WARNING")
            return None, None

        if not quantity_text.isdigit() or int(quantity_text) <= 0:
            QMessageBox.warning(self.window, "Invalid Format", "Quantity must be an integer greater than 0!")
            self.generalUI.update_info_log("Invalid Format: Quantity must be an integer greater than 0!", level="WARNING")
            return None, None

        if not sample_date:
            QMessageBox.warning(self.window, "Missing Information", "Please enter the Sample Date!")
            self.generalUI.update_info_log("Missing Information: Please enter the Sample Date!", level="WARNING")
            return None, None

        qdate_val = self.generalUI.input_sample_date.date()
        year_yyyy, yymmdd = self._parse_sample_date(qdate_val)
        if not year_yyyy or not yymmdd:
            QMessageBox.warning(
                self.window,
                "Invalid Date Format",
                "Sample Date format is invalid! Please use dd/mm/yyyy (e.g., 24/11/2026) or yymmdd."
            )
            self.generalUI.update_info_log(f"Invalid Sample Date format: {sample_date}", level="WARNING")
            return None, None
        sample_date_str = qdate_val.toString("dd/MM/yyyy")

        element_type = self.generalUI.input_element_type.currentText().strip()
        line = self.generalUI.input_line.currentText().strip()

        info_data = {
            "eft_machine": self.generalUI.input_eft_machine.currentText(),
            "test_order_no": test_order_no,  # Optional field
            "charge_no": charge_no,
            "task_name": self.generalUI.input_task_name.currentText(),
            "element_type": element_type,
            "line": line,
            "process": self.generalUI.input_process.currentText(),
            "axis": self.generalUI.input_axis.currentText(),
            "requester_by": self.generalUI.input_requester.currentText(),
            "quantity": int(quantity_text),
            "sample_date": sample_date,
            "remark": self.generalUI.input_remark.toPlainText().strip()
        }

        # 3. Get default force setting (N) from element_config.xml
        default_force = self.config_reader.get_force_by_element(element_type) or ""

        # 4. Generate base name depending on whether Test Order No. is provided
        # - Without Order No.: yymmddChargeNo_Elementtype_Line
        # - With Order No.: OrderNoyymmddChargeNo_Elementtype_Line
        if test_order_no:
            base_name = f"{test_order_no}{yymmdd}{charge_no}_{element_type}_{line}"
        else:
            base_name = f"{yymmdd}{charge_no}_{element_type}_{line}"

        # 5. Build target directory path: <TestFiles>/<YYYY>/<base_name>/
        root_dir = path_cfg.get("TestFiles", "")
        target_dir = os.path.join(root_dir, year_yyyy, base_name)
        os.makedirs(target_dir, exist_ok=True)

        default_filename = f"{base_name}.json"
        save_path, _ = QFileDialog.getSaveFileName(
            self.window,
            "Save Test File",
            os.path.join(target_dir, default_filename),
            "JSON Files (*.json)"
        )

        if not save_path:
            return None, None  # User canceled the save dialog

        # 6. Save JSON file and reload the created data
        try:
            self.test_file_manager.create_test_json(save_path, info_data, default_setting_n=default_force)
            test_data = self.test_file_manager.load_test_json(save_path)

            self.generalUI.current_json_path = save_path
            self.generalUI.current_test_data = test_data

            return save_path, test_data

        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Failed to create file:\n{str(e)}")
            self.generalUI.update_info_log(f"Failed to create file: {save_path} - {str(e)}", level="ERROR")
            return None, None

    def handle_create_file(self):
        """
        Create and save the JSON test file while remaining on the Create tab.
        """
        save_path, _ = self.build_and_save_json()
        if save_path:
            QMessageBox.information(self.window, "Success", f"Created file successfully:\n{save_path}")
            self.generalUI.update_info_log(f"Created test file: {save_path}", level="SUCCESS")

    def handle_start_testing(self):
        """
        Save the JSON file, then automatically switch to the Testing tab and load the data.
        """
        save_path, test_data = self.build_and_save_json()
        if not save_path or not test_data:
            return

        if not test_data.get("elements"):
            QMessageBox.warning(self.window, "No Samples Found", "The test file does not contain any samples to be tested!")
            self.generalUI.update_info_log(f"No Samples Found: {save_path}", level="WARNING")
            return

        # Start session: switches to Testing tab, populates Result table, and loads the first element
        self.generalUI.testing_ui.start_session(save_path, test_data)
        self.generalUI.update_test_information(test_data)
        self.generalUI.update_info_log(f"Created and started test: {save_path}", level="INFO")