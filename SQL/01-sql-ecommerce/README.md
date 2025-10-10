# 📊 Data Faker & SQL Indexing Performance Project

This project demonstrates how indexing can dramatically improve SQL query performance, using a realistic e-commerce dataset generated with Python. It combines data generation, relational schema design, and query analysis to showcase practical database optimization techniques.

---

## 📦 Overview

The project is divided into two main components:

### 1. Synthetic Data Generation
A Python script creates realistic CSV files representing:
- Customers
- Products
- Orders
- Order items
- Payments

This data simulates the structure and behavior of a transactional e-commerce system and serves as the foundation for SQL experimentation.

### 2. SQL Performance Analysis
Using PostgreSQL, the project explores how query execution plans change before and after adding indexes. The focus is on understanding scan types, row counts, and cost estimates using `EXPLAIN ANALYZE`.

---

## 🧪 Data Generation

The dataset includes:
- 100 customers with names, emails, and signup dates  
- 100 products with SKUs, names, and prices  
- 200 orders linked to customers  
- 500 order items connecting products to orders  
- 200 payments, one per order  

To generate the data:
```bash
pip install faker

Then run the Python script. The output consists of five CSV files saved in the current directory.


## 🗃️ Database Schema

The PostgreSQL schema defines five core tables:

### `customers`
- `customer_id` (PK) – Unique identifier
- `name` – Full name
- `email` – Email address
- `signup_date` – Date of registration

### `products`
- `product_id` (PK) – Unique identifier
- `sku` – Stock keeping unit
- `name` – Product name
- `price` – Unit price

### `orders`
- `order_id` (PK) – Unique identifier
- `customer_id` (FK) – Linked to `customers.customer_id`
- `order_date` – Timestamp of order

### `order_items`
- `item_id` (PK) – Unique identifier
- `order_id` (FK) – Linked to `orders.order_id`
- `product_id` (FK) – Linked to `products.product_id`
- `quantity` – Number of units

### `payments`
- `payment_id` (PK) – Unique identifier
- `order_id` (FK) – Linked to `orders.order_id`
- `amount` – Payment amount
- `payment_date` – Timestamp of payment


## 🧠 SQL Queries

Here are some example queries included in the project:

### Monthly Revenue Aggregation
```sql
SELECT DATE_TRUNC('month', payment_date) AS month,
       SUM(amount) AS total_revenue
FROM payments
GROUP BY month
ORDER BY month;

## Top 5 Customers by Total Spending

SELECT c.customer_id,
       c.name,
       SUM(p.amount) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN payments p ON o.order_id = p.order_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC
LIMIT 5;

## Products Never Purchased

SELECT p.product_id,
       p.name
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.product_id IS NULL;


---

### ⚙️ Performance Analysis

```md
## ⚙️ Performance Analysis

To evaluate query performance, the project compares execution plans before and after indexing `orders.customer_id`.

### Files:
- `outputs/explain_before_index.txt`
- `outputs/explain_after_index.txt`

### Key Observations:
- **Before Indexing**: PostgreSQL uses **sequential scans**, resulting in higher row counts and cost estimates.
- **After Indexing**: The planner switches to **index scans**, significantly reducing scanned rows and improving execution time.

### Example:
```sql
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE customer_id = 42;

This query benefits from the index by narrowing down the search efficiently