import os
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QWidget,
    QTabWidget,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QMessageBox,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from services.config_reader import ConfigReader
from services.test_file_manager import TestFileManager
from services.chart_service import ChartService
from services.excel_export_service import ExcelExportService


class DataUI:
    def __init__(self, window: QWidget, generalUI):
        self.window = window
        self.config_reader = ConfigReader()
        self.TestFileManager = TestFileManager()
        self.test_data = None
        self.json_path = None
        self.current_figure = None
        self.generalUI = generalUI

        self.widget_init()

        self.default_cycle = self.config_reader.get_default_cycle()
        self.adjust_force = self.config_reader.get_adjust_force()

    def widget_init(self):
        """
        Initialize widgets in the "Data" tab, bind sub-tabs (Table / Analysis),
        setup embedded chart container, and connect button signals.
        """
        self.tabWidget_3 = getattr(self.generalUI, "tabWidget_3", None) or self.window.findChild(QTabWidget, "tabWidget_3")
        self.widget_analysis = getattr(self.generalUI, "widget_analysis", None) or self.window.findChild(QWidget, "widget_analysis")
        self.analysis_btn = getattr(self.generalUI, "analysis_btn", None) or self.window.findChild(QPushButton, "analysis_btn")
        self.save_fig_btn = getattr(self.generalUI, "save_fig_btn", None) or self.window.findChild(QPushButton, "save_fig_btn")
        self.export_btn = getattr(self.generalUI, "export_btn", None) or self.window.findChild(QPushButton, "export_btn")

        if self.widget_analysis:
            if self.widget_analysis.layout() is None:
                self.analysis_layout = QVBoxLayout(self.widget_analysis)
                self.analysis_layout.setContentsMargins(4, 4, 4, 4)
            else:
                self.analysis_layout = self.widget_analysis.layout()

        self.table_model = QStandardItemModel()
        self.headers = ["Element No.", "Setting (N)", "Cycles (rpm)", "Result", "Failure", "Input Person", "Remark"]
        self.table_model.setHorizontalHeaderLabels(self.headers)
        if self.generalUI.table_results_2:
            self.generalUI.table_results_2.setModel(self.table_model)

        if self.generalUI.close_btn_2:
            self.generalUI.close_btn_2.clicked.connect(self.handle_close)
        if self.analysis_btn:
            self.analysis_btn.clicked.connect(self.handle_analysis)
        if self.save_fig_btn:
            self.save_fig_btn.setEnabled(False)
            self.save_fig_btn.clicked.connect(self.handle_save_fig)
        if self.export_btn:
            self.export_btn.clicked.connect(self.handle_export)

    def start_session(self, json_path, test_data):
        """Load test data into the Data tab (Table view) when Monitor is triggered."""
        self.json_path = json_path
        self.test_data = test_data
        self._clear_analysis_chart()

        if self.generalUI.tab_widget:
            self.generalUI.tab_widget.setCurrentIndex(3)
        if self.tabWidget_3:
            self.tabWidget_3.setCurrentIndex(0)

        self.refresh_table()

    def refresh_table(self):
        """Populate QTableView with element results from self.test_data['elements']."""
        self.table_model.setRowCount(0)
        if not self.test_data:
            return

        for el in self.test_data.get("elements", []):
            remark_val = el.get("remark") if el.get("remark") is not None else el.get("input_remark_testing", "")
            row = [
                QStandardItem(str(el.get("element_no", ""))),
                QStandardItem(str(el.get("setting_N", ""))),
                QStandardItem(str(el.get("cycles_rpm", ""))),
                QStandardItem(str(el.get("result", ""))),
                QStandardItem(str(el.get("failure", ""))),
                QStandardItem(str(el.get("input_person", ""))),
                QStandardItem(str(remark_val)),
            ]
            self.table_model.appendRow(row)

    def _get_active_test_data(self):
        """Return active test_data in DataUI, or fallback to generalUI.current_test_data."""
        if self.test_data:
            return self.test_data
        return getattr(self.generalUI, "current_test_data", None)

    def _clear_analysis_chart(self):
        """Remove existing chart widgets from widget_analysis and reset Save Fig button."""
        self.current_figure = None
        if self.save_fig_btn:
            self.save_fig_btn.setEnabled(False)

        if hasattr(self, "analysis_layout") and self.analysis_layout:
            while self.analysis_layout.count():
                item = self.analysis_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    def handle_analysis(self):
        """Switch to Analysis sub-tab and embed distribution figure generated by ChartService."""
        test_data = self._get_active_test_data()
        if not test_data or "elements" not in test_data:
            QMessageBox.warning(self.window, "No Data", "Please load a test order first!")
            return

        try:
            fig = ChartService.build_break_distribution_figure(test_data)
        except ValueError as e:
            QMessageBox.information(self.window, "Analysis Notice", str(e))
            return

        if self.tabWidget_3:
            self.tabWidget_3.setCurrentIndex(1)

        self._clear_analysis_chart()

        canvas = FigureCanvas(fig)
        if hasattr(self, "analysis_layout"):
            self.analysis_layout.addWidget(canvas)
        canvas.draw()

        self.current_figure = fig
        if self.save_fig_btn:
            self.save_fig_btn.setEnabled(True)

        if hasattr(self.generalUI, "update_info_log"):
            self.generalUI.update_info_log("Plotted break distribution chart.", level="INFO")

    def handle_save_fig(self):
        """Prompt save dialog and delegate image export to ChartService."""
        if not self.current_figure:
            QMessageBox.warning(self.window, "No Chart", "Please click 'Analysis' to generate a chart first!")
            return

        test_data = self._get_active_test_data() or {}
        info = test_data.get("test_info", {})

        if self.json_path:
            base_name = f"{os.path.splitext(os.path.basename(self.json_path))[0]}_Analysis"
            default_dir = os.path.dirname(self.json_path)
        else:
            base_name = f"{info.get('charge_no', 'EFT')}_{info.get('element_type', 'Chart')}_Analysis"
            default_dir = ""

        save_path, _ = QFileDialog.getSaveFileName(
            self.window,
            "Save Distribution Chart",
            os.path.join(default_dir, f"{base_name}.png"),
            "PNG Image (*.png);;JPEG Image (*.jpg);;PDF Document (*.pdf)"
        )
        if not save_path:
            return

        try:
            ChartService.save_figure(self.current_figure, save_path, dpi=300)
            QMessageBox.information(self.window, "Saved", f"Chart saved successfully:\n{save_path}")

            if hasattr(self.generalUI, "update_info_log"):
                self.generalUI.update_info_log(f"Saved analysis chart: {save_path}", level="SUCCESS")

        except Exception as e:
            QMessageBox.critical(self.window, "Save Failed", f"Failed to save chart:\n{str(e)}")
            if hasattr(self.generalUI, "update_info_log"):
                self.generalUI.update_info_log(f"Save chart error: {str(e)}", level="ERROR")

    def handle_export(self):
        """Prompt save dialog and delegate Excel report creation to ExcelExportService."""
        test_data = self._get_active_test_data()
        if not test_data or "elements" not in test_data:
            QMessageBox.warning(self.window, "No Data", "Please load a test order first!")
            return

        info = test_data.get("test_info", {})
        if self.json_path:
            base_name = os.path.splitext(os.path.basename(self.json_path))[0]
            default_dir = os.path.dirname(self.json_path)
        else:
            base_name = f"{info.get('charge_no', 'EFT')}_{info.get('element_type', 'Report')}"
            default_dir = ""

        save_path, _ = QFileDialog.getSaveFileName(
            self.window,
            "Export Test Results to Excel",
            os.path.join(default_dir, f"{base_name}.xlsx"),
            "Excel Files (*.xlsx)"
        )
        if not save_path:
            return

        try:
            ExcelExportService.export_test_report(test_data, save_path)
            QMessageBox.information(self.window, "Export Successful", f"Exported Excel report successfully:\n{save_path}")

            if hasattr(self.generalUI, "update_info_log"):
                self.generalUI.update_info_log(f"Exported Excel report: {save_path}", level="SUCCESS")

        except Exception as e:
            QMessageBox.critical(self.window, "Export Failed", f"Failed to export Excel file:\n{str(e)}")
            if hasattr(self.generalUI, "update_info_log"):
                self.generalUI.update_info_log(f"Excel export error: {str(e)}", level="ERROR")

    def reset_testing_ui(self):
        """Clear table, chart, and state variables in the Data tab."""
        self.json_path = None
        self.test_data = None
        self.current_index = 0

        if hasattr(self.generalUI, "current_json_path"):
            self.generalUI.current_json_path = None
        if hasattr(self.generalUI, "current_test_data"):
            self.generalUI.current_test_data = None

        if hasattr(self, "table_model") and self.table_model:
            self.table_model.setRowCount(0)

        self._clear_analysis_chart()

        if self.tabWidget_3:
            self.tabWidget_3.setCurrentIndex(0)

        if self.generalUI.information_test:
            self.generalUI.information_test.clear()

        if hasattr(self.generalUI, "update_progress_bar"):
            self.generalUI.update_progress_bar(None)

    def handle_close(self):
        """Close the current Data view session and clear UI without exiting the app."""
        reply = QMessageBox.question(
            self.window,
            "Confirm Close",
            "Do you want to close this test view?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reset_testing_ui()

            if hasattr(self.generalUI, "update_info_log"):
                self.generalUI.update_info_log("Closed current test view on Data tab.", level="INFO")

            if self.generalUI.tab_widget:
                self.generalUI.tab_widget.setCurrentIndex(0)