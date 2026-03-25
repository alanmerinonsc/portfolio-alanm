# DFaker -- Fake Data Generator
# This program allows you to generate custom CSV datasets using a simple UI.
# You can define fields (columns) and choose how each one generates data.
#
# Field Options:
# - sequence: Incremental numbers (1, 2, 3...)
# - faker: Realistic fake data (name, email, address, etc.)
# - alphanumeric: Random letters and numbers (set length)
# - boolean: True / False values
# - list: Custom values (e.g. Open, Closed, Pending)
#         Mode:
#           - random: picks randomly
#           - cycle: loops in order
# - range: Numeric values between start and end
#         Types:
#           - int: whole numbers
#           - float: decimal numbers
#
# Additional Settings:
# - Output folder selection
# - File name
# - Record count
# - CSV delimiter (comma or pipe)
#
# Useful for testing, prototyping, and generating mock data.

import csv
import os
import random
import string
from faker import Faker
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ====
# GLOBAL CONFIGURATION
# ====

OUTPUT_FOLDER = "./output"
DEFAULT_FILE_NAME = "output.csv"
CSV_DELIMITER = "|"
RECORD_COUNT = 50

# ====
# MODEL
# ====

class SchemaModel:
    def __init__(self):
        self.fields = []
        self.file_name = DEFAULT_FILE_NAME

    def add_field(self, field_name, source):
        self.fields.append({
            "fieldName": field_name,
            "source": source
        })

# ====
# FAKER METHODS HELPER
# ====

def get_faker_methods():
    priority_methods = [
        "name", "first_name", "last_name", "email", "user_name",
        "phone_number", "address", "city", "state", "country",
        "company", "job", "date", "date_time", "uuid4",
        "word", "sentence", "text", "url",
        "ipv4", "ipv6", "credit_card_number", "iban", "password"
    ]

    fake = Faker()
    methods = set()

    import inspect
    for provider in fake.get_providers():
        for name, member in inspect.getmembers(provider):
            if not name.startswith("_") and callable(member):
                methods.add(name)

    remaining = sorted(methods - set(priority_methods))
    return priority_methods + remaining

FAKER_METHODS = get_faker_methods()  # cache once

# ====
# CONTROLLER
# ====

fake = Faker()

class FakeDataGenerator:

    def __init__(self, model, record_count):
        self.model = model
        self.record_count = record_count

        self.generators = {
            "sequence": self._sequence,
            "faker": self._faker,
            "alphanumeric": self._alphanumeric,
            "boolean": self._boolean,
            "list": self._list,
            "range": self._range
        }

    def _sequence(self, source, seq):
        return seq

    def _faker(self, source, seq):
        method = getattr(fake, source.get("method", "word"), None)
        return method() if method else "N/A"

    def _alphanumeric(self, source, seq):
        length = int(source.get("length", 8))
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _boolean(self, source, seq):
        return random.choice([True, False])

    def _list(self, source, seq):
        values = source.get("values", [])
        mode = source.get("mode", "random")

        if not values:
            return None

        if mode == "cycle":
            return values[(seq - 1) % len(values)]

        return random.choice(values)

    def _range(self, source, seq):
        start = float(source.get("start", 0))
        end = float(source.get("end", 100))
        value_type = source.get("value_type", "int")

        if value_type == "float":
            return round(random.uniform(start, end), 2)

        return random.randint(int(start), int(end))

    def generate_value(self, source, seq):
        return self.generators[source["type"]](source, seq)

    def generate_rows(self):
        rows = []
        for seq in range(1, self.record_count + 1):
            row = {}
            for field in self.model.fields:
                row[field["fieldName"]] = self.generate_value(field["source"], seq)
            rows.append(row)
        return rows

# ====
# VIEW (CSV)
# ====

class CSVView:
    @staticmethod
    def write(rows, folder, filename, delimiter):
        if not rows:
            return

        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=rows[0].keys(),
                delimiter=delimiter
            )
            writer.writeheader()
            writer.writerows(rows)

        return path

# ====
# VIEW (GUI)
# ====

class GUIView:

    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.root.title("Fake Data Generator")

        self.build_main()

    def build_main(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid()

        # -------------------------
        # FILE CONFIG
        # -------------------------

        ttk.Label(frame, text="File Name").grid(row=0, column=0)
        self.file_name = ttk.Entry(frame)
        self.file_name.insert(0, DEFAULT_FILE_NAME)
        self.file_name.grid(row=0, column=1)

        ttk.Label(frame, text="Output Folder").grid(row=1, column=0)
        self.output_path = ttk.Entry(frame)
        self.output_path.insert(0, OUTPUT_FOLDER)
        self.output_path.grid(row=1, column=1)

        ttk.Button(frame, text="Browse", command=self.select_folder).grid(row=1, column=2)

        ttk.Label(frame, text="Records").grid(row=2, column=0)
        self.record_count = ttk.Entry(frame)
        self.record_count.insert(0, "50")
        self.record_count.grid(row=2, column=1)

        ttk.Label(frame, text="Delimiter").grid(row=3, column=0)
        self.delimiter = ttk.Combobox(frame, values=["|", ","])
        self.delimiter.set(CSV_DELIMITER)
        self.delimiter.grid(row=3, column=1)

        # -------------------------
        # ACTIONS
        # -------------------------

        ttk.Button(frame, text="Add Field", command=self.open_field_window).grid(row=4, column=0)
        ttk.Button(frame, text="Remove Field", command=self.remove_field).grid(row=4, column=1)
        ttk.Button(frame, text="Generate CSV", command=self.generate).grid(row=4, column=2)

        # -------------------------
        # FIELD LIST
        # -------------------------

        self.field_list = tk.Listbox(frame, width=60)
        self.field_list.grid(row=5, column=0, columnspan=3)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, folder)

    def remove_field(self):
        selected = self.field_list.curselection()

        if not selected:
            messagebox.showwarning("Warning", "Select a field to remove")
            return

        index = selected[0]
        del self.app.model.fields[index]
        self.field_list.delete(index)

    def open_field_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add Field")

        ttk.Label(win, text="Field Name").grid(row=0, column=0)
        field_name = ttk.Entry(win)
        field_name.grid(row=0, column=1)

        ttk.Label(win, text="Type").grid(row=1, column=0)
        type_combo = ttk.Combobox(
            win,
            values=["sequence", "faker", "alphanumeric", "boolean", "list", "range"]
        )
        type_combo.grid(row=1, column=1)

        ttk.Label(win, text="Faker Method").grid(row=2, column=0)
        faker_combo = ttk.Combobox(win, values=FAKER_METHODS)
        faker_combo.grid(row=2, column=1)

        ttk.Label(win, text="Length").grid(row=3, column=0)
        length_entry = ttk.Entry(win)
        length_entry.grid(row=3, column=1)

        ttk.Label(win, text="List Values").grid(row=4, column=0)
        list_entry = ttk.Entry(win)
        list_entry.grid(row=4, column=1)

        ttk.Label(win, text="Mode").grid(row=5, column=0)
        mode_combo = ttk.Combobox(win, values=["random", "cycle"])
        mode_combo.grid(row=5, column=1)

        ttk.Label(win, text="Range Start").grid(row=6, column=0)
        start_entry = ttk.Entry(win)
        start_entry.grid(row=6, column=1)

        ttk.Label(win, text="Range End").grid(row=7, column=0)
        end_entry = ttk.Entry(win)
        end_entry.grid(row=7, column=1)

        ttk.Label(win, text="Range Type").grid(row=8, column=0)
        range_type = ttk.Combobox(win, values=["int", "float"])
        range_type.grid(row=8, column=1)

        def save_field():
            name = field_name.get()
            t = type_combo.get()

            if not name or not t:
                messagebox.showerror("Error", "Field name and type required")
                return

            source = {"type": t}

            if t == "faker":
                source["method"] = faker_combo.get() or "word"

            if t == "alphanumeric":
                source["length"] = length_entry.get() or 8

            if t == "list":
                source["values"] = [v.strip() for v in list_entry.get().split(",") if v.strip()]
                source["mode"] = mode_combo.get() or "random"

            if t == "range":
                source["start"] = start_entry.get()
                source["end"] = end_entry.get()
                source["value_type"] = range_type.get() or "int"

            self.app.model.add_field(name, source)
            self.field_list.insert(tk.END, f"{name} ({t})")

            win.destroy()

        ttk.Button(win, text="Save", command=save_field).grid(row=9, column=1)

    def generate(self):
        try:
            self.app.model.file_name = self.file_name.get()
            record_count = int(self.record_count.get())
            output_folder = self.output_path.get()
            delimiter = self.delimiter.get()

            generator = FakeDataGenerator(self.app.model, record_count)
            rows = generator.generate_rows()

            path = CSVView.write(rows, output_folder, self.app.model.file_name, delimiter)

            messagebox.showinfo("Success", f"File created:\n{path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

# ====
# APP
# ====

class FakeDataApp:
    def __init__(self):
        self.model = SchemaModel()

    def run(self):
        root = tk.Tk()
        GUIView(root, self)
        root.mainloop()

# ====
# ENTRY POINT
# ====

if __name__ == "__main__":
    app = FakeDataApp()
    app.run()