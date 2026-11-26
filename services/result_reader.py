import os
import re


class ResultReader:
    @staticmethod
    def get_cycles_from_folder(folder_path: str, element_no: int, machine_type: str = "TYPE_1") -> str:
        """
        Read the final cycles value for a specific element_no from the mapped result folder.
        Supports multiple machine log formats via machine_type.
        """
        if not folder_path or not os.path.isdir(folder_path):
            raise FileNotFoundError("Result folder does not exist or is invalid.")

        if machine_type == "TYPE_1":
            return ResultReader._read_woe_type1(folder_path, element_no)
        elif machine_type == "TYPE_2":
            # Placeholder for the second machine type in the future
            raise NotImplementedError("Machine Type 2 parser is not implemented yet.")
        else:
            raise ValueError(f"Unsupported machine type: {machine_type}")

    @staticmethod
    def _read_woe_type1(folder_path: str, element_no: int) -> str:
        """
        Type 1 Machine: Each sample corresponds to '<element_no>.Woe' (e.g., 1.Woe, 2.Woe).
        Extracts the last recorded cycles value from the file.
        """
        # Find matching file case-insensitively (e.g., '1.Woe' or '1.woe')
        target_name = f"{element_no}.woe"
        matched_file = None

        for fname in os.listdir(folder_path):
            if fname.lower() == target_name:
                matched_file = os.path.join(folder_path, fname)
                break

        if not matched_file or not os.path.isfile(matched_file):
            raise FileNotFoundError(f"Result file '{element_no}.Woe' not found in:\n{folder_path}")

        # Read file content (try utf-8 first, fallback to cp1252/latin1 for industrial machine logs)
        lines = []
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                with open(matched_file, "r", encoding=enc) as f:
                    lines = [line.strip() for line in f if line.strip()]
                break
            except UnicodeDecodeError:
                continue

        if not lines:
            raise ValueError(f"File '{element_no}.Woe' is empty.")

        # Scan from the last line upwards to extract the final recorded cycles value
        for line in reversed(lines):
            # Extract all integer numbers in the line
            numbers = re.findall(r"\d+", line)
            if numbers:
                # If the line has multiple columns (e.g., Time | Cycles | Force),
                # adjust index if Cycles is not the first/last number.
                # Default: take the largest integer on the last data line (usually Cycles)
                cycles_val = max(numbers, key=lambda x: int(x))
                return str(int(cycles_val))

        raise ValueError(f"Could not find any numeric cycles value in '{element_no}.Woe'.")
    
    @staticmethod
    def validate_result_folder(folder_path: str, expected_charge_no: str) -> tuple[bool, str]:
        """
        Verify that the selected result folder name contains the expected Charge No.
        Example folder: '261102A853After Deburring' -> must contain 'A853'.
        """
        if not folder_path or not os.path.isdir(folder_path):
            return False, "Result folder does not exist or is invalid."

        charge_no = str(expected_charge_no or "").strip()
        if not charge_no:
            return False, "Current test file does not have a valid Charge No."

        folder_name = os.path.basename(os.path.normpath(folder_path))
        if charge_no.lower() not in folder_name.lower():
            return (
                False,
                f"Charge No. mismatch!\n"
                f"- Expected Charge No.: {charge_no}\n"
                f"- Selected folder: {folder_name}"
            )

        return True, ""