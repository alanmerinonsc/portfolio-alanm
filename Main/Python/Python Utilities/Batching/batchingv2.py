##Enhanced version
# This enhanced script splits large CSV files into smaller batches of a specified size 
# while cleaning header names. It removes all special characters from headers but 
# preserves underscores and numbers, ensuring uniqueness and readability. Each output 
# file retains the cleaned header row, making the resulting datasets easier to process 
# and integrate. The script can handle multiple CSVs from an input folder and saves 
# the cleaned, split files into an output folder.

import os
import csv
import re
from pathlib import Path

# ===
# CONFIGURATION VARIABLES
# ===

INPUT_FOLDER = r"C:/Users/alan/Python Tools/Batching/input"     # Folder with large CSVs
OUTPUT_FOLDER = r"C:/Users/alan/Python Tools/Batching/output"   # Where split files will be stored
BATCH_SIZE = 50000                                                                               # Records per output file

# ====
# HEADER CLEANING (only keep letters, digits, and underscores)
# ====

_allow_alnum_underscore = re.compile(r'[^A-Za-z0-9_]+')

def clean_headers(headers):
    """
    Remove any character that is not a letter, digit, or underscore.
    Keeps underscores and numbers. Does not replace—just removes.
    Ensures uniqueness and non-empty names (col_1, col_2, ...) if needed.
    """
    cleaned = []
    seen = {}
    empty_counter = 1

    for h in headers:
        s = "" if h is None else str(h).strip()

        # Remove everything except A-Z a-z 0-9 and underscore
        s = _allow_alnum_underscore.sub('', s)

        # If empty after cleaning, assign a placeholder
        if not s:
            s = f"col_{empty_counter}"
            empty_counter += 1

        # Ensure unique header names if cleaning caused collisions
        if s not in seen:
            seen[s] = 1
            cleaned.append(s)
        else:
            seen[s] += 1
            cleaned.append(f"{s}_{seen[s]}")

    return cleaned

# ====
# FUNCTION
# ====

def split_csv_file(input_file_path, output_folder, batch_size):
    file_name = Path(input_file_path).stem
    extension = Path(input_file_path).suffix

    os.makedirs(output_folder, exist_ok=True)

    # Use utf-8-sig to automatically strip BOM (handles ï»¿ cases)
    with open(input_file_path, mode='r', newline='', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)
        header = next(reader)

        # Clean the header as requested
        header = clean_headers(header)

        file_count = 1
        record_count = 0

        output_file = open(
            os.path.join(output_folder, f"{file_name}_{file_count}{extension}"),
            mode='w',
            newline='',
            encoding='utf-8'
        )
        writer = csv.writer(output_file)
        writer.writerow(header)

        for row in reader:
            # (Fix HTML artifact) use '>' here, not '&gt;'
            if record_count > 0 and record_count % batch_size == 0:
                output_file.close()
                file_count += 1

                output_file = open(
                    os.path.join(output_folder, f"{file_name}_{file_count}{extension}"),
                    mode='w',
                    newline='',
                    encoding='utf-8'
                )
                writer = csv.writer(output_file)
                writer.writerow(header)

            writer.writerow(row)
            record_count += 1

        output_file.close()

    print(f"{file_name} → Generated {file_count} file(s)")

# ====
# PROCESS MULTIPLE FILES
# ====

def process_all_files(input_folder, output_folder, batch_size):
    for file in os.listdir(input_folder):
        if file.lower().endswith(".csv"):
            full_path = os.path.join(input_folder, file)
            print(f"Processing: {file}")
            split_csv_file(full_path, output_folder, batch_size)

if __name__ == "__main__":
    process_all_files(INPUT_FOLDER, OUTPUT_FOLDER, BATCH_SIZE)