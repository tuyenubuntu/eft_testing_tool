import os
import json
from datetime import datetime
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QWidget,
    QDateEdit,
    QPushButton,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from services.config_reader import ConfigReader
from services.test_file_manager import TestFileManager


class TestOrderUI:
    def __init__(self, window: QWidget, generalUI):
        self.window = window
        self.generalUI = generalUI
        self.config_reader = ConfigReader()

        # Added "Machine" column
        self.headers = ["No.", "Machine", "File name", "Element", "Process", "Create Date", "Finished Date"]
        self.widget_init()

    def widget_init(self):
        """
        Bind widgets on the Test Orders tab, set default date range (start to end of current year),
        and connect the Filter button signal.
        """
        self.date_from = getattr(self.generalUI, "date_from", None) or self.window.findChild(QDateEdit, "date_from")
        self.date_to = getattr(self.generalUI, "date_to", None) or self.window.findChild(QDateEdit, "date_to")
        self.filter_btn = getattr(self.generalUI, "filter_btn", None) or self.window.findChild(QPushButton, "filter_btn")
        self.table_orders = getattr(self.generalUI, "table_orders", None) or self.window.findChild(QWidget, "table_orders")
        # Select entire row when clicking and connect double-click signal
        if self.table_orders:
            self.table_orders.setSelectionBehavior(QTableView.SelectRows)
            self.table_orders.setSelectionMode(QTableView.SingleSelection)
            self.table_orders.doubleClicked.connect(self.handle_row_double_clicked)

        # Set default date range: Jan 1 to Dec 31 of the current year
        current_year = datetime.now().year
        if self.date_from:
            self.date_from.setCalendarPopup(True)
            self.date_from.setDate(QDate(current_year, 1, 1))
        if self.date_to:
            self.date_to.setCalendarPopup(True)
            self.date_to.setDate(QDate(current_year, 12, 31))

        # Initialize table model/headers
        if isinstance(self.table_orders, QTableView):
            self.table_model = QStandardItemModel()
            self.table_model.setHorizontalHeaderLabels(self.headers)
            self.table_orders.setModel(self.table_model)
            self.table_orders.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.table_orders.horizontalHeader().setStretchLastSection(True)
        elif isinstance(self.table_orders, QTableWidget):
            self.table_orders.setColumnCount(len(self.headers))
            self.table_orders.setHorizontalHeaderLabels(self.headers)
            self.table_orders.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.table_orders.horizontalHeader().setStretchLastSection(True)

        # Connect Filter button
        if self.filter_btn:
            self.filter_btn.clicked.connect(self.handle_filter)

        # Load initial data for the current year automatically
        self.handle_filter()

    def _parse_created_datetime(self, created_str):
        """
        Parse 'created_at' string from JSON (e.g., '2026-11-24 13:24:59') into a datetime object.
        """
        if not created_str:
            return None
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(created_str.strip(), fmt)
            except ValueError:
                continue
        return None

    def _scan_test_files(self, start_date, end_date):
        """
        Recursively scan all JSON test files in the configured TestFiles directory,
        filter by date range [start_date, end_date], and sort newest first.
        """
        path_cfg = self.config_reader.get_path_configs()
        root_dir = path_cfg.get("TestFiles", "")
        if not root_dir or not os.path.exists(root_dir):
            return []

        records = []
        for dirpath, _, filenames in os.walk(root_dir):
            for fname in filenames:
                if not fname.lower().endswith(".json"):
                    continue

                full_path = os.path.join(dirpath, fname)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    if "test_info" not in data:
                        continue

                    info = data.get("test_info", {})
                    created_str = info.get("created_at", "")
                    created_dt = self._parse_created_datetime(created_str)

                    # Fallback to file modification time if created_at is missing
                    if created_dt is None:
                        created_dt = datetime.fromtimestamp(os.path.getmtime(full_path))
                        created_str = created_dt.strftime("%Y-%m-%d %H:%M:%S")

                    # Filter by date range
                    record_date = created_dt.date()
                    if not (start_date <= record_date <= end_date):
                        continue

                    # Determine Finished Date (if status is Finished)
                    finished_date = info.get("finished_at", "")
                    if not finished_date and info.get("status") == "Finished":
                        finished_date = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime("%Y-%m-%d %H:%M:%S")

                    records.append({
                        "sort_key": created_dt,
                        "machine": info.get("eft_machine", ""),
                        "file_name": os.path.splitext(fname)[0],
                        "full_path": full_path,
                        "element": info.get("element_type", ""),
                        "process": info.get("process", ""),
                        "create_date": created_str,
                        "finished_date": finished_date,
                    })
                except Exception:
                    continue

        # Sort newest first
        records.sort(key=lambda x: x["sort_key"], reverse=True)
        return records

    def handle_filter(self):
        """
        Filter test orders between date_from and date_to and populate table_orders.
        """
        if not self.date_from or not self.date_to or not self.table_orders:
            return

        start_date = self.date_from.date().toPython()
        end_date = self.date_to.date().toPython()

        if start_date > end_date:
            QMessageBox.warning(self.window, "Invalid Date Range", "'From' date cannot be later than 'To' date!")
            return

        records = self._scan_test_files(start_date, end_date)
        self._populate_table(records)

        if hasattr(self.generalUI, "update_info_log"):
            self.generalUI.update_info_log(
                f"Filtered {len(records)} test order(s) from {start_date} to {end_date}.",
                level="INFO"
            )

    def _populate_table(self, records):
        """
        Render filtered records into table_orders.
        Since records are sorted newest first, numbering increases upwards (oldest = 1, newest = N).
        """
        self.filtered_records = records  # Store records to retrieve full_path on double-click
        total_records = len(records)

        if isinstance(self.table_orders, QTableView):
            self.table_model.setRowCount(0)
            for idx, rec in enumerate(records):
                order_num = total_records - idx  # Ascending upwards (N down to 1)
                row_items = [
                    QStandardItem(str(order_num)),
                    QStandardItem(rec["machine"]),
                    QStandardItem(rec["file_name"]),
                    QStandardItem(rec["element"]),
                    QStandardItem(rec["process"]),
                    QStandardItem(rec["create_date"]),
                    QStandardItem(rec["finished_date"]),
                ]
                for item in row_items:
                    item.setEditable(False)
                row_items[0].setTextAlignment(Qt.AlignCenter)
                row_items[1].setTextAlignment(Qt.AlignCenter)
                self.table_model.appendRow(row_items)

        elif isinstance(self.table_orders, QTableWidget):
            self.table_orders.setRowCount(0)
            for idx, rec in enumerate(records):
                order_num = total_records - idx  # Ascending upwards (N down to 1)
                row_idx = self.table_orders.rowCount()
                self.table_orders.insertRow(row_idx)
                values = [
                    str(order_num),
                    rec["machine"],
                    rec["file_name"],
                    rec["element"],
                    rec["process"],
                    rec["create_date"],
                    rec["finished_date"],
                ]
                for col_idx, val in enumerate(values):
                    cell = QTableWidgetItem(val)
                    cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                    if col_idx in (0, 1):
                        cell.setTextAlignment(Qt.AlignCenter)
                    self.table_orders.setItem(row_idx, col_idx, cell)

    def handle_row_double_clicked(self, index):
        """
        Load the selected JSON test file when double-clicking a row in table_orders
        and switch directly to the Testing tab.
        """
        row = index.row()
        if not hasattr(self, "filtered_records") or row < 0 or row >= len(self.filtered_records):
            return

        selected_record = self.filtered_records[row]
        file_path = selected_record.get("full_path", "")

        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self.window, "File Not Found", f"The test file no longer exists:\n{file_path}")
            return

        try:
            test_data = TestFileManager.load_test_json(file_path)

            # Update shared state on generalUI
            self.generalUI.current_json_path = file_path
            self.generalUI.current_test_data = test_data

            # Update right-hand Test Information panel & bottom Progress Bar
            if hasattr(self.generalUI, "update_test_information"):
                self.generalUI.update_test_information(test_data)
            if hasattr(self.generalUI, "update_progress_bar"):
                self.generalUI.update_progress_bar(test_data)

            # Start testing session (switches to Testing tab, populates Result table, loads next untested element)
            if hasattr(self.generalUI, "testing_ui") and self.generalUI.testing_ui:
                self.generalUI.testing_ui.start_session(file_path, test_data)

            if hasattr(self.generalUI, "update_info_log"):
                self.generalUI.update_info_log(
                    f"Opened test order from history: {os.path.basename(file_path)}",
                    level="INFO"
                )

        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Failed to load test file:\n{str(e)}")
            if hasattr(self.generalUI, "update_info_log"):
                self.generalUI.update_info_log(f"Error opening test order: {str(e)}", level="ERROR")