# This script splits large CSV files into smaller batches of a specified size, 
# preserving the header row in each output file. It can process multiple CSVs 
# from an input folder and save the resulting batch files into an output folder, 
# making large datasets easier to handle and manage.

import os
import csv
from pathlib import Path

# ===
# CONFIGURATION VARIABLES
# ===
 
INPUT_FOLDER = r"C:/Users/alan/Python Tools/Batching/input"     # Folder with large CSVs
OUTPUT_FOLDER = r"C:/Users/alan/Python Tools/Batching/output"      # Where split files will be stored
BATCH_SIZE = 50000                              # Records per output file
 
# ===
# FUNCTION
# ===
 
def split_csv_file(input_file_path, output_folder, batch_size):
    file_name = Path(input_file_path).stem
    extension = Path(input_file_path).suffix
 
    os.makedirs(output_folder, exist_ok=True)
 
    with open(input_file_path, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)
 
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
 
# ===
# PROCESS MULTIPLE FILES
# ===
 
def process_all_files(input_folder, output_folder, batch_size):
    for file in os.listdir(input_folder):
        if file.lower().endswith(".csv"):
            full_path = os.path.join(input_folder, file)
            print(f"Processing: {file}")
            split_csv_file(full_path, output_folder, batch_size)
 
if __name__ == "__main__":
    process_all_files(INPUT_FOLDER, OUTPUT_FOLDER, BATCH_SIZE)