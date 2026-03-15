# JSON Schema Formatter UI

# Overview:
# This script provides a Tkinter-based UI that formats JSON objects into schema arrays. 
# It infers data types (BIT, INT, DECIMAL, STRING, DATETIME, OBJECT, ARRAY, etc.), 
# uppercases all string values for preprocessing, and outputs schema fields with 
# uppercase values for fieldName, nullable ("TRUE"/"FALSE"), and parseType.

# Usage:
# - Paste a JSON object (single record) in the input box.
# - Click "Format" to produce a schema array with fieldName, nullable, and parseType.
# - Converts all *values* that are strings to UPPERCASE (attribute names are preserved).
# - Additionally, uppercases the *output schema values* for:
#     - fieldName  -> STRING (uppercased)
#     - nullable   -> "TRUE"/"FALSE" (uppercased string)
#     - parseType  -> STRING (uppercased)
# - "nullable" checkbox sets all to false when checked.
# - "Clear" empties both input and output.

# Type inference (mapped names):
#   - bool   -> BIT
#   - int    -> INT
#   - float  -> DECIMAL
#   - str    -> STRING (or DATETIME if detected)
#   - None   -> NULL
#   - dict   -> OBJECT
#   - list   -> ARRAY<T> (homogeneous), ARRAY<MIXED> (heterogeneous), ARRAY<ANY> (empty)

# Datetime detection:
#   - Supports ISO 8601 and common formats such as:
#     YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS[.fff][Z|±HH:MM],
#     MM/DD/YYYY, DD/MM/YYYY, YYYY/MM/DD, etc.


import json
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# ------------------------
# Helpers
# ------------------------

ISO_LIKE_PATTERNS = [
    # 2024-12-31
    r"^\d{4}-\d{2}-\d{2}$",
    # 2024-12-31T23:59:59
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",
    # 2024-12-31T23:59:59.123
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$",
    # 2024-12-31T23:59:59Z
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
    # 2024-12-31T23:59:59+05:30
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?[+-]\d{2}:\d{2}$",
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$"
]


COMMON_DATETIME_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%m/%d/%Y %H:%M",

    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",

    "%m/%d/%Y %I:%M:%S %p",   # <-- 12-hour format
    "%m/%d/%Y %I:%M %p",

    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
]



def looks_like_datetime(s: str) -> bool:
    """Heuristically detect datetimes from strings."""
    if not isinstance(s, str):
        return False

    # Trim and collapse multiple spaces (handles "  11:50:35  AM" etc.)
    txt = " ".join(s.strip().split())
    if not txt:
        return False

    # Fast path: try true ISO formats first (e.g., 2026-03-11T11:50:35+00:00)
    # Handle trailing Z for fromisoformat; only if it looks ISO-like (YYYY-MM-DD...)
    iso_like = bool(re.match(r"^\d{4}-\d{2}-\d{2}", txt))
    if iso_like:
        iso_candidate = txt[:-1] + "+00:00" if txt.endswith("Z") else txt
        try:
            datetime.fromisoformat(iso_candidate)
            return True
        except Exception:
            pass

    # Shortcut accept for some common ISO-ish regexes, if you want that behavior
    for pat in ISO_LIKE_PATTERNS:
        if re.match(pat, txt):
            return True

    # For non-ISO slash dates that may include 'T' and/or 'Z'
    # Build a small set of candidates to try with strptime:
    # - original
    # - replace trailing Z with +00:00 (for %z)
    # - replace T with space (common in exports)
    # - both replacements together
    candidates = {txt}
    if txt.endswith("Z"):
        candidates.add(txt[:-1] + "+00:00")
    if "T" in txt and "/" in txt.split("T", 1)[0]:
        candidates.add(txt.replace("T", " "))
        if txt.endswith("Z"):
            candidates.add(txt.replace("T", " ")[:-1] + "+00:00")

    # Try common explicit formats
    for cand in candidates:
        for fmt in COMMON_DATETIME_FORMATS:
            try:
                datetime.strptime(cand, fmt)
                return True
            except Exception:
                continue

    return False


def to_uppercase_values(value):
    """
    Recursively convert only *string* values to uppercase.
    Do not alter keys (field names).
    """
    if isinstance(value, str):
        return value.upper()
    elif isinstance(value, list):
        return [to_uppercase_values(v) for v in value]
    elif isinstance(value, dict):
        return {k: to_uppercase_values(v) for k, v in value.items()}
    else:
        return value

# ------------------------
# Type inference utilities
# ------------------------

def infer_scalar_type(value):
    """Infer type for non-list, non-dict values (mapped names)."""
    if isinstance(value, bool):
        return "BIT"
    elif value is None:
        return "NULL"
    elif isinstance(value, int):
        return "INT"
    elif isinstance(value, float):
        return "DOUBLE"
    elif isinstance(value, str):
     return "DATETIME" if looks_like_datetime(value) else "STRING"

    elif isinstance(value, str):
        # If it LOOKS like a datetime, promote to DATETIME
        return "STRING" #if looks_like_datetime(value) else "STRING"
    else:
        return "UNKNOWN"

def infer_array_element_type(lst):
    """Infer a unified element type for a list, if possible (mapped names)."""
    if not lst:
        return "ANY"

    element_types = []
    for el in lst:
        if isinstance(el, list):
            subtype = infer_array_element_type(el)
            element_types.append(f"ARRAY<{subtype}>")
        elif isinstance(el, dict):
            element_types.append("OBJECT")
        else:
            element_types.append(infer_scalar_type(el))

    unique_types = set(element_types)
    if len(unique_types) == 1:
        return unique_types.pop()
    else:
        return "MIXED"

def infer_parse_type(value):
    """Infer parseType for any JSON value (mapped names)."""
    if isinstance(value, list):
        subtype = infer_array_element_type(value)
        return f"ARRAY<{subtype}>"
    elif isinstance(value, dict):
        return "OBJECT"
    else:
        return infer_scalar_type(value)

def format_schema_from_record(record, nullable_default=True):
    """
    Given a top-level dict `record`, return a list of {fieldName, nullable, parseType}.
    Values are transformed to uppercase first (strings only) to satisfy requirements.
    """
    if not isinstance(record, dict):
        raise ValueError("Top-level JSON must be an object with attribute-value pairs.")

    # Uppercase values (not keys) before type inference (affects DATETIME/string heuristics but not numbers/bools)
    record_upper = {k: to_uppercase_values(v) for k, v in record.items()}

    schema = []
    for key, value in record_upper.items():
        schema.append({
            "fieldName": str(key),
            "nullable": bool(nullable_default),
            "parseType": infer_parse_type(value),
        })
    return schema

# ------------------------
# NEW: Uppercase output schema values
# ------------------------

def uppercase_schema_fields(schema_rows):
    """
    Convert output values on fieldName, nullable, and parseType to uppercase strings:
      - fieldName -> FIELDNAME (string)
      - nullable  -> "TRUE" / "FALSE" (string)
      - parseType -> already uppercase, but enforce .upper()
    Returns a NEW list (does not mutate original).
    """
    upper_rows = []
    for row in schema_rows:
        field_name = str(row.get("fieldName", "")).upper()
        nullable_val = row.get("nullable", True)
        # Convert boolean to uppercase string "TRUE"/"FALSE"
        nullable_str = True if bool(nullable_val) else False
        parse_type = str(row.get("parseType", "")).upper()

        upper_rows.append({
            "fieldName": field_name,
            "nullable": nullable_str,
            "parseType": parse_type,
        })
    return upper_rows

# ------------------------
# UI Handlers
# ------------------------

def on_format():
    """Handle Format button click."""
    raw = input_text.get("1.0", tk.END).strip()
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)

    if not raw:
        messagebox.showinfo("Info", "Please paste a JSON object in the input area.")
        output_text.config(state="disabled")
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        messagebox.showerror("Invalid JSON", f"Could not parse JSON:\n{e}")
        output_text.insert(tk.END, f"Error: Could not parse JSON:\n{e}\n")
        output_text.config(state="disabled")
        return

    try:
        nullable_default = not nullable_false_var.get()  # checkbox sets ALL false if checked
        schema = format_schema_from_record(data, nullable_default=nullable_default)
        schema_upper = uppercase_schema_fields(schema)   # <-- apply the requested uppercasing on output

        pretty = json.dumps(schema_upper, indent=2, ensure_ascii=False)
        output_text.insert(tk.END, pretty + "\n")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")
        output_text.insert(tk.END, f"Error: {e}\n")

    output_text.config(state="disabled")

def on_clear():
    """Handle Clear button click: clears input and output."""
    input_text.delete("1.0", tk.END)
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.config(state="disabled")

# ------------------------
# Build UI
# ------------------------

root = tk.Tk()
root.title("JSON Schema Formatter")

# Responsive grid
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(5, weight=1)

# Header
header = ttk.Label(root, text="JSON Schema Formatter", font=("Segoe UI", 14, "bold"))
header.grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")

# Input label + text
input_label = ttk.Label(root, text="Input JSON (object):")
input_label.grid(row=1, column=0, padx=12, pady=(4, 2), sticky="w")

input_frame = ttk.Frame(root)
input_frame.grid(row=2, column=0, padx=12, pady=(0, 6), sticky="nsew")
input_frame.columnconfigure(0, weight=1)
input_frame.rowconfigure(0, weight=1)

mono_font = ("Consolas", 11)
input_text = tk.Text(input_frame, wrap="word", height=12, font=mono_font, undo=True)
input_text.grid(row=0, column=0, sticky="nsew")

input_scroll = ttk.Scrollbar(input_frame, orient="vertical", command=input_text.yview)
input_scroll.grid(row=0, column=1, sticky="ns")
input_text.config(yscrollcommand=input_scroll.set)

# Controls: Format, Clear, Checkbox
controls = ttk.Frame(root)
controls.grid(row=3, column=0, padx=12, pady=6, sticky="w")

format_btn = ttk.Button(controls, text="Format", command=on_format)
format_btn.grid(row=0, column=0, padx=(0, 8))

clear_btn = ttk.Button(controls, text="Clear", command=on_clear)
clear_btn.grid(row=0, column=1, padx=(0, 16))

nullable_false_var = tk.BooleanVar(value=False)
nullable_chk = ttk.Checkbutton(
    controls,
    text="Set 'nullable' to false for all",
    variable=nullable_false_var
)
nullable_chk.grid(row=0, column=2)

# Output label + text (read-only)
output_label = ttk.Label(root, text="Formatted Schema:")
output_label.grid(row=4, column=0, padx=12, pady=(8, 2), sticky="w")

output_frame = ttk.Frame(root)
output_frame.grid(row=5, column=0, padx=12, pady=(0, 12), sticky="nsew")
output_frame.columnconfigure(0, weight=1)
output_frame.rowconfigure(0, weight=1)

output_text = tk.Text(output_frame, wrap="none", height=12, font=mono_font, state="disabled")
output_text.grid(row=0, column=0, sticky="nsew")

output_scroll = ttk.Scrollbar(output_frame, orient="vertical", command=output_text.yview)
output_scroll.grid(row=0, column=1, sticky="ns")
output_text.config(yscrollcommand=output_scroll.set)

output_hscroll = ttk.Scrollbar(output_frame, orient="horizontal", command=output_text.xview)
output_hscroll.grid(row=1, column=0, columnspan=2, sticky="ew")
output_text.config(xscrollcommand=output_hscroll.set)

# Run
if __name__ == "__main__":
    root.minsize(700, 600)
    root.mainloop()
