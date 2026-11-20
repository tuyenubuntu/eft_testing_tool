import os
import sys
from datetime import datetime


class LogServices:
    def __init__(self, save_to_file=True, log_dir="app_logs"):
        """
        Manager 
        """
        self.save_to_file = save_to_file
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.log_folder = os.path.join(base_dir, log_dir)
        if self.save_to_file:
            os.makedirs(self.log_folder, exist_ok=True)

    def format_log(self, message, level="INFO"):
        """
        Format
        Returen tuple: (plain_text, html_text)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_upper = level.upper()

        color_map = {
            "INFO": "#1f2937",      # Đen xám
            "SUCCESS": "#15803d",   # Xanh lá đậm
            "WARNING": "#b45309",   # Cam đậm
            "ERROR": "#b91c1c",     # Đỏ đậm
        }
        color = color_map.get(level_upper, "#1f2937")

        plain_text = f"[{timestamp}] [{level_upper}] {message}"
        html_text = (
            f'<span style="color:#6b7280;">[{timestamp}]</span> '
            f'<b style="color:{color};">[{level_upper}]</b> '
            f'<span style="color:#111827;">{message}</span>'
        )

        if self.save_to_file:
            self._write_to_file(plain_text)

        return plain_text, html_text

    def _write_to_file(self, plain_text):
        """Record (ex: 2026-11-18.log)"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        log_file_path = os.path.join(self.log_folder, f"eft_tool_{today_str}.log")
        try:
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write(plain_text + "\n")
        except Exception:
            pass