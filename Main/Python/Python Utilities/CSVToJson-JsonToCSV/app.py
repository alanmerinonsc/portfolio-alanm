import csv
import json
from pathlib import Path

# ====
# CONFIGURATION
# ====
INPUT_FOLDER = r"C:\Python Utilities\JsonToCSV\input"
INPUT_FILE = "activity_time_sample.csv"

OUTPUT_FOLDER = r"C:\Python Utilities\JsonToCSV\output"
OUTPUT_FILE = "wfm_activity_payload.txt"  # .txt allowed for JSON payloads

MODE = "csv_to_json"  # options: csv_to_json | json_to_csv
ENCODING = "utf-8"

# ====
# FUNCTIONS
# ====
def csv_to_json(input_path, output_path):
    with input_path.open(mode="r", encoding=ENCODING, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        data = list(reader)

    with output_path.open(mode="w", encoding=ENCODING) as output_file:
        json.dump(data, output_file, indent=2, ensure_ascii=False)

    print(f"CSV > JSON written to: {output_path}")


def json_to_csv(input_path, output_path):
    with input_path.open(mode="r", encoding=ENCODING) as json_file:
        data = json.load(json_file)

    if not isinstance(data, list) or not data:
        raise ValueError("JSON must be a non-empty list of objects")

    with output_path.open(mode="w", encoding=ENCODING, newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"JSON > CSV written to: {output_path}")


# ====
# MAIN EXECUTION
# ====
def main():
    input_path = Path(INPUT_FOLDER) / INPUT_FILE
    output_path = Path(OUTPUT_FOLDER) / OUTPUT_FILE

    if not input_path.exists():
        raise FileNotFoundError(f"Error - Input file not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if MODE == "csv_to_json":
        csv_to_json(input_path, output_path)

    elif MODE == "json_to_csv":
        json_to_csv(input_path, output_path)

    else:
        raise ValueError("MODE must be 'csv_to_json' or 'json_to_csv'")


if __name__ == "__main__":
    main()