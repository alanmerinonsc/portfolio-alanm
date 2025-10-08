Data Faker & SQL Indexing Performance Project
This project demonstrates how indexing can dramatically improve SQL query performance, using a realistic e-commerce dataset generated with Python. It combines data generation, relational schema design, and query analysis to showcase practical database optimization techniques.

Overview
The project is divided into two main components:
1. Synthetic Data Generation
A Python script creates realistic CSV files representing customers, products, orders, order items, and payments. This data simulates the structure and behavior of a transactional e-commerce system and serves as the foundation for SQL experimentation.
2. SQL Performance Analysis
Using PostgreSQL, the project explores how query execution plans change before and after adding indexes. The focus is on understanding scan types, row counts, and cost estimates using EXPLAIN ANALYZE.

Data Generation
The dataset includes:
• 100 customers with names, emails, and signup dates
• 100 products with SKUs, names, and prices
• 200 orders linked to customers
• 500 order items connecting products to orders
• 200 payments, one per order
To generate the data, run the Python script after installing the Faker library (pip install faker). The output consists of five CSV files saved in the current directory.

Database Schema
The PostgreSQL schema defines five core tables: customers, products, orders, order_items, and payments. Foreign key relationships and basic indexes are included to support query performance and integrity.
SQL Queries
The project includes several example queries to demonstrate SQL proficiency:
• Monthly revenue aggregation
• Top 5 customers by total spending
• Identification of products never purchased

Performance Analysis
To evaluate query performance, the project compares execution plans before and after creating an index on orders.customer_id. The results are saved in:
• outputs/explain_before_index.txt
• outputs/explain_after_index.txt

These files reveal how the query planner shifts from sequential scans to index scans, significantly reducing the number of rows scanned and lowering execution cost.

By combining realistic data generation with targeted SQL queries and performance diagnostics, this project illustrates the tangible benefits of indexing in relational databases. It provides a hands-on demonstration of how thoughtful schema design and query tuning can lead to more efficient data retrieval—an essential skill for any SQL practitioner.
