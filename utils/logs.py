# utils/logs.py
import csv
from datetime import datetime

def log_session(output_path: str, entry: dict):
    """
    Appends a new entry to the session log CSV.
    """
    fieldnames = ["timestamp", "shape", "quantity", "head_mode", "api_total_mg", "unit_weight_mg"]
    entry["timestamp"] = datetime.now().isoformat(timespec='seconds')

    try:
        with open(output_path, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(entry)
    except Exception as e:
        print(f"Logging error: {e}")
