# CSV Splitter & Header Cleaner

# Overview:
# This script processes large CSV files by splitting them into smaller batches 
# and cleaning header names. It removes all special characters from headers 
# while preserving underscores and numbers, ensuring unique and valid column names. 
# Each output file retains the cleaned header row, making the resulting datasets 
# consistent, easier to manage, and ready for downstream processing.

# Usage:
# - Configure INPUT_FOLDER, OUTPUT_FOLDER, and BATCH_SIZE at the top of the script.
# - Place large CSV files in the input folder.
# - Run the script to automatically split each file into smaller batches.
# - Headers are cleaned to remove invalid characters, with placeholders (col_1, col_2, …) 
#   assigned if empty, and suffixes added if duplicates occur.

# Features:
# - Splits CSV files into batches of a specified size.
# - Preserves and cleans headers for consistency.
# - Handles multiple CSV files in a folder.
# - Uses UTF-8-SIG encoding to strip BOM artifacts.
# - Ensures uniqueness of header names after cleaning.

import os
import glob
import sys
import pandas as pd

# =========================
# CONFIG — EDIT THESE
# =========================
DIRECTORY = r"C:\Users\alan\Python Tools\ScanValues\input"   # e.g., r"C:\Data\to\scan" or "./files"
COLUMN    = "TargetMedia"                      # e.g., "Email", "Status"
VALUE     = "SURVEY CALLS"           # the exact value to look for
CASE_INSENSITIVE = False                  # True/False
SHOW_ROWS = 5                            # show up to N matching rows per file; 0 to hide
PATTERNS  = ["*.csv"] # which files to scan ["*.csv", "*.xlsx", "*.xls"]
SHEET     = None                         # Excel sheet name; set None to scan all sheets
# =========================

def _normalize(series: pd.Series, lower: bool):
    s = series.astype(str).str.strip()
    return s.str.lower() if lower else s

def _normalize_value(value: str, lower: bool):
    v = str(value).strip()
    return v.lower() if lower else v

def _find_files(directory, patterns):
    files = []
    for pat in patterns:
        files.extend(glob.glob(os.path.join(directory, pat)))
    return sorted(files)

def _scan_csv(path, column, value, lower):
    matches = 0
    sample = None
    try:
        for chunk in pd.read_csv(path, dtype=str, chunksize=100_000, encoding_errors="replace"):
            if column not in chunk.columns:
                return -1, None
            col = _normalize(chunk[column], lower)
            val = _normalize_value(value, lower)
            m = chunk[col.eq(val)]
            matches += len(m)
            if SHOW_ROWS and matches > 0 and sample is None:
                sample = m.head(SHOW_ROWS)
    except Exception:
        df = pd.read_csv(path, dtype=str, encoding_errors="replace")
        if column not in df.columns:
            return -1, None
        col = _normalize(df[column], lower)
        val = _normalize_value(value, lower)
        m = df[col.eq(val)]
        matches = len(m)
        if SHOW_ROWS and matches > 0:
            sample = m.head(SHOW_ROWS)
    return matches, sample

def _scan_excel(path, column, value, lower, sheet_name=None):
    total = 0
    sample = None
    try:
        engine = "openpyxl" if path.lower().endswith(".xlsx") else "xlrd"
        xls = pd.ExcelFile(path, engine=engine)
    except Exception as e:
        print(f"⚠️  Could not open '{os.path.basename(path)}': {e}")
        return 0, None

    sheets = [sheet_name] if sheet_name else xls.sheet_names
    seen_column_anywhere = False
    for sn in sheets:
        df = xls.parse(sn, dtype=str)
        if column not in df.columns:
            continue
        seen_column_anywhere = True
        col = _normalize(df[column], lower)
        val = _normalize_value(value, lower)
        m = df[col.eq(val)]
        total += len(m)
        if SHOW_ROWS and total > 0 and sample is None:
            sample = m.head(SHOW_ROWS)

    if not seen_column_anywhere:
        return -1, None
    return total, sample

def main():
    directory = os.path.abspath(DIRECTORY)
    if not os.path.isdir(directory):
        print(f"❌ Directory not found: {directory}")
        sys.exit(1)

    files = _find_files(directory, PATTERNS)
    if not files:
        print(f"⚠️  No files found in {directory} for patterns: {', '.join(PATTERNS)}")
        sys.exit(0)

    print(f"🔎 Scanning {len(files)} file(s) in: {directory}")
    print(f"   Column: '{COLUMN}' | Value: '{VALUE}' | Case-insensitive: {CASE_INSENSITIVE}")
    if SHEET:
        print(f"   Excel sheet: {SHEET}")

    results = []
    missing_col = []
    total_files_with_matches = 0
    total_matches = 0

    for path in files:
        try:
            if path.lower().endswith(".csv"):
                count, sample = _scan_csv(path, COLUMN, VALUE, CASE_INSENSITIVE)
            elif path.lower().endswith((".xlsx", ".xls")):
                count, sample = _scan_excel(path, COLUMN, VALUE, CASE_INSENSITIVE, SHEET)
            else:
                continue

            if count == -1:
                missing_col.append(path)
            else:
                results.append((path, count, sample))
                if count > 0:
                    total_files_with_matches += 1
                    total_matches += count
        except Exception as e:
            print(f"⚠️  Error reading '{os.path.basename(path)}': {e}")

    print("\n=== Results ===")
    for path, count, sample in results:
        base = os.path.basename(path)
        if count > 0:
            print(f"✅ {base} — {count} match(es)")
            if SHOW_ROWS and sample is not None:
                with pd.option_context("display.max_columns", None, "display.width", 200):
                    print(sample)
        else:
            print(f"—  {base} — 0 matches")

    if missing_col:
        print(f"\nℹ️  Files missing the column '{COLUMN}':")
        for p in missing_col:
            print(f"   • {os.path.basename(p)}")

    print("\n=== Summary ===")
    print(f"Files scanned: {len(files)}")
    print(f"Files with matches: {total_files_with_matches}")
    print(f"Total matching rows: {total_matches}")

if __name__ == "__main__":
    main()