# 🛍️ Data Faker – Synthetic E-Commerce Dataset Generator

**Data Faker** is a Python script that generates realistic, synthetic datasets for a fictional e-commerce platform. It uses the [Faker](https://faker.readthedocs.io/en/master/) library to simulate customer profiles, product listings, order histories, and payment records, then exports the data into structured CSV files.

---

## 📦 Generated Datasets

This script creates five CSV files, but it can be edited and manipulated as needed, so the desired data can be obtained.

| File Name        | Description |
|------------------|-------------|
| `customers.csv`  | 100 fake customers with names, unique emails, and account creation dates spanning the past two years. |
| `products.csv`   | 100 products with SKU codes, randomized names, and prices ranging from $10 to $500. |
| `orders.csv`     | 200 orders linked to customers, each with a total amount, order date within the past year, and a status (`pending`, `completed`, or `cancelled`). |
| `order_items.csv`| 500 line items connecting products to orders, specifying quantity and unit price. |
| `payments.csv`   | One payment per order, with payment date, amount, and status (`paid`, `failed`, or `refunded`). |

All timestamps are generated to reflect realistic business activity.

---

## 🛠️ Technologies Used

- Python 3
- `faker` library
- Built-in `csv` module

---

## 🚀 How to Run

1. Install dependencies:
   ```bash
   pip install faker

2. Run the script: python data_faker.py

3. Output files will be saved in the current directory. A confirmation message will appear once generation is complete.

🎯 Use CasesData Faker is ideal for:- Testing data pipelines
- Practicing analysis with pandas
- Simulating database imports for data modeling and testing
- Building mock dashboards and APIs