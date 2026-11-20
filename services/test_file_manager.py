import json
import os
from datetime import datetime


class TestFileManager:
    @staticmethod
    def create_test_json(save_path, info_data, default_setting_n=""):
        """
        create_test_json: create a JSON file for test data based on the provided information.
        :param save_path: str, the path where the JSON file will be saved.
        :param info_data: dict, a dictionary containing test information.
        :param default_setting_n: str, the default force setting (N) for the test
        """
        quantity = int(info_data.get("quantity", 0))

        # Initialize 1 -> quantity
        elements_list = []
        for idx in range(1, quantity + 1):
            elements_list.append({
                "element_no": idx,
                "cycles_rpm": "",
                "result": "",
                "failure": "",
                "input_person": "",
                "remark": ""
            })

        # structure payload
        payload = {
            "test_info": {
                "eft_machine": info_data.get("eft_machine", ""),
                "test_order_no": info_data.get("test_order_no", ""),
                "charge_no": info_data.get("charge_no", ""),
                "task_name": info_data.get("task_name", ""),
                "element_type": info_data.get("element_type", ""),
                "first_force_setting_n": default_setting_n,
                "line": info_data.get("line", ""),
                "process": info_data.get("process", ""),
                "axis": info_data.get("axis", ""),
                "requester_by": info_data.get("requester_by", ""),
                "quantity": quantity,
                "sample_date": info_data.get("sample_date", ""),
                "remark": info_data.get("remark", ""),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Created"
            },
            "elements": elements_list
        }

        # Ensure the directory exists before writing the file
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)

        return save_path
    
    @staticmethod
    def load_test_json(file_path):
        """
        Read a JSON test file and return its content as a dictionary.
        :param file_path: str, the path to the JSON file to read.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check if the JSON structure is valid
        if "test_info" not in data or "elements" not in data:
            raise ValueError("File JSON does not match the expected format of the EFT-Testing Tool!")

        return data
    
    @staticmethod
    def save_test_json(file_path, data):
        """Read a JSON test file and return its content as a dictionary."""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary to save as JSON.")
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)