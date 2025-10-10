import os
import json

## Tool to merge multiple JSON files in a directory into a single JSON array. 
## Use case: Files from S3 (indentified as Json) without extensions.

def merge_json_files(directory, output_file):
    merged_data = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Process only files without extensions
        if os.path.isfile(file_path) and '.' not in filename:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    merged_data.append(data)
                    print(f"Merged: {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

    # Write the merged JSON array to output file
    with open(output_file, 'w', encoding='utf-8') as out_file:
        json.dump(merged_data, out_file, indent=2)
    print(f"All files merged into {output_file}")

# Run the merge
merge_json_files(".", "merged_output.json")
print("Files have been merged.")