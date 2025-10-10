# 🧰 JSON Merger Tool

A lightweight Python utility to merge multiple JSON files from a directory into a single JSON array. Ideal for processing files downloaded from S3 buckets that lack file extensions.

## 📦 Features

- Merges JSON files without extensions into one array  
- Handles read errors gracefully  
- Outputs a well-formatted JSON file  
- Designed for S3-style file dumps

## 🛠️ Usage

### 1. Prerequisites

Ensure you have Python 3 installed.

### 2. Setup

Clone or copy the script into your working directory.

### 3. Run the Script

```bash
python merge_json.py
```

By default, it merges all extension-less files in the current directory and writes the result to `merged_output.json`.

### 4. Customize Directory or Output

You can modify the call to `merge_json_files()` at the bottom of the script:

```python
merge_json_files("/path/to/json/files", "output.json")
```

## 📁 Input Requirements

- Files must be valid JSON  
- Files must have no extensions (e.g., `abc123`, not `abc123.json`)  
- All files should reside in the same directory

## 📤 Output

- A single JSON file containing an array of merged objects  
- Example output:

```json
[
  { "id": 1, "name": "Alice" },
  { "id": 2, "name": "Bob" }
]
```

## ⚠️ Error Handling

- Files that fail to parse as JSON are skipped with a warning  
- The script prints progress and error messages to the console

## 📄 License

This project is open-source and available under the MIT License.