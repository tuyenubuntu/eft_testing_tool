from collections import Counter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


class ExcelExportService:
    @staticmethod
    def export_test_report(test_data: dict, save_path: str):
        """
        Generate and save a formatted Excel (.xlsx) report containing:
        - Sheet 1 ('Test_Result'): Metadata, element results table, and summary formulas.
        - Sheet 2 ('Break_Analysis'): Summary of broken samples grouped by Force Setting (N).
        """
        if not test_data or "elements" not in test_data:
            raise ValueError("Invalid or empty test data.")

        info = test_data.get("test_info", {})
        elements = test_data.get("elements", [])

        wb = openpyxl.Workbook()

        # ==========================================
        # SHEET 1: Test_Result
        # ==========================================
        ws = wb.active
        ws.title = "Test_Result"

        title_font = Font(name="Calibri", size=14, bold=True, color="1F4E78")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        meta_label_font = Font(name="Calibri", size=10, bold=True)
        meta_fill = PatternFill(start_color="F2F4F8", end_color="F2F4F8", fill_type="solid")
        break_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
        not_break_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

        thin_border = Border(
            left=Side(style="thin", color="BFBFBF"),
            right=Side(style="thin", color="BFBFBF"),
            top=Side(style="thin", color="BFBFBF"),
            bottom=Side(style="thin", color="BFBFBF"),
        )

        # Report Title
        ws["A1"] = "EFT ENDURANCE TEST REPORT"
        ws["A1"].font = title_font
        ws.merge_cells("A1:G1")

        # Metadata Section
        meta_rows = [
            ("EFT Machine:", info.get("eft_machine", ""), "Line:", info.get("line", "")),
            ("Test Order No.:", info.get("test_order_no", ""), "Process:", info.get("process", "")),
            ("Charge No.:", info.get("charge_no", ""), "Axis:", info.get("axis", "")),
            ("Task Name:", info.get("task_name", ""), "Requester:", info.get("requester_by", "")),
            ("Element Type:", info.get("element_type", ""), "Sample Date:", info.get("sample_date", "")),
            ("Initial Force (N):", info.get("first_force_setting_n", ""), "Status:", info.get("status", "")),
            ("Created At:", info.get("created_at", ""), "Finished At:", info.get("finished_at", "")),
            ("Remark:", info.get("remark", ""), "Quantity:", info.get("quantity", len(elements))),
        ]

        for idx, (k1, v1, k2, v2) in enumerate(meta_rows, start=3):
            ws.cell(row=idx, column=1, value=k1).font = meta_label_font
            ws.cell(row=idx, column=1).fill = meta_fill
            ws.cell(row=idx, column=2, value=v1)

            ws.cell(row=idx, column=4, value=k2).font = meta_label_font
            ws.cell(row=idx, column=4).fill = meta_fill
            ws.cell(row=idx, column=5, value=v2)

            for col in (1, 2, 4, 5):
                ws.cell(row=idx, column=col).border = thin_border

        # Element Results Table Header
        table_start_row = 12
        headers = ["Element No.", "Setting (N)", "Cycles (rpm)", "Result", "Failure", "Input Person", "Remark"]
        for col_idx, text in enumerate(headers, start=1):
            cell = ws.cell(row=table_start_row, column=col_idx, value=text)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        # Element Rows
        for i, el in enumerate(elements, start=1):
            r = table_start_row + i
            try:
                setting_val = int(float(el.get("setting_N", 0))) if str(el.get("setting_N", "")).strip() else ""
            except ValueError:
                setting_val = el.get("setting_N", "")

            try:
                cycles_val = int(str(el.get("cycles_rpm", "")).replace(",", "")) if str(el.get("cycles_rpm", "")).strip() else ""
            except ValueError:
                cycles_val = el.get("cycles_rpm", "")

            result_val = str(el.get("result", "")).strip()
            remark_val = el.get("remark") if el.get("remark") is not None else el.get("input_remark_testing", "")

            row_vals = [
                el.get("element_no", i),
                setting_val,
                cycles_val,
                result_val,
                el.get("failure", ""),
                el.get("input_person", ""),
                remark_val,
            ]

            for col_idx, val in enumerate(row_vals, start=1):
                cell = ws.cell(row=r, column=col_idx, value=val)
                cell.border = thin_border
                if col_idx in (1, 2, 3, 4):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                if col_idx == 3 and isinstance(val, int):
                    cell.number_format = "#,##0"

                if col_idx == 4:
                    if result_val.lower() == "break":
                        cell.fill = break_fill
                        cell.font = Font(bold=True, color="9C0006")
                    elif result_val.lower() == "not break":
                        cell.fill = not_break_fill
                        cell.font = Font(bold=True, color="006100")

        # Summary Formulas
        last_data_row = table_start_row + len(elements)
        summary_row = last_data_row + 2
        ws.cell(row=summary_row, column=1, value="Total Samples:").font = meta_label_font
        ws.cell(row=summary_row, column=2, value=f"=COUNTA(A{table_start_row+1}:A{last_data_row})")

        ws.cell(row=summary_row + 1, column=1, value="Total Break:").font = meta_label_font
        ws.cell(row=summary_row + 1, column=2, value=f'=COUNTIF(D{table_start_row+1}:D{last_data_row},"Break")')

        ws.cell(row=summary_row + 2, column=1, value="Total Not Break:").font = meta_label_font
        ws.cell(row=summary_row + 2, column=2, value=f'=COUNTIF(D{table_start_row+1}:D{last_data_row},"Not break")')

        col_widths = {1: 16, 2: 18, 3: 18, 4: 16, 5: 18, 6: 20, 7: 25}
        for col_idx, width in col_widths.items():
            ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = width

        # ==========================================
        # SHEET 2: Break_Analysis
        # ==========================================
        ws_break = wb.create_sheet(title="Break_Analysis")
        ws_break["A1"] = "BREAK SAMPLES SUMMARY BY FORCE SETTING"
        ws_break["A1"].font = title_font

        ws_break.cell(row=3, column=1, value="Setting (N)").font = header_font
        ws_break.cell(row=3, column=1).fill = header_fill
        ws_break.cell(row=3, column=2, value="Break Count").font = header_font
        ws_break.cell(row=3, column=2).fill = header_fill

        broken_elements = [el for el in elements if str(el.get("result", "")).strip().lower() == "break"]
        force_counts = Counter()
        for el in broken_elements:
            try:
                force_counts[int(float(el.get("setting_N", 0)))] += 1
            except ValueError:
                pass

        for idx, f_val in enumerate(sorted(force_counts.keys()), start=4):
            c1 = ws_break.cell(row=idx, column=1, value=f_val)
            c2 = ws_break.cell(row=idx, column=2, value=force_counts[f_val])
            c1.border = thin_border
            c2.border = thin_border
            c1.alignment = Alignment(horizontal="center")
            c2.alignment = Alignment(horizontal="center")

        ws_break.column_dimensions["A"].width = 18
        ws_break.column_dimensions["B"].width = 18

        wb.save(save_path)