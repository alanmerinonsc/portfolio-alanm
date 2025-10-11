import csv, random
from faker import Faker
from datetime import datetime

fake = Faker()

NUM_CUSTOMERS = 100
NUM_PRODUCTS = 100
NUM_ORDERS = 200
NUM_ORDER_ITEMS = 500
NUM_PAYMENTS = NUM_ORDERS

# --- Customers ---
with open('customers.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['customer_id', 'name', 'email', 'created_at'])
    for i in range(1, NUM_CUSTOMERS + 1):
        writer.writerow([
            i,
            fake.name(),
            fake.unique.email(),
            fake.date_time_between(start_date='-2y', end_date='now').isoformat()
        ])

# --- Products ---
with open('products.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['product_id', 'sku', 'name', 'price'])
    for i in range(1, NUM_PRODUCTS + 1):
        writer.writerow([
            i,
            f'SKU{i:05}',
            fake.word().capitalize() + " " + fake.word().capitalize(),
            round(random.uniform(10, 500), 2)
        ])

# --- Orders ---
order_totals = {}
with open('orders.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['order_id', 'customer_id', 'order_date', 'total_amount', 'status'])
    for i in range(1, NUM_ORDERS + 1):
        total = round(random.uniform(50, 1500), 2)
        order_totals[i] = total
        writer.writerow([
            i,
            random.randint(1, NUM_CUSTOMERS),
            fake.date_between(start_date='-1y', end_date='today').isoformat(),
            total,
            random.choice(['pending', 'completed', 'cancelled'])
        ])

# --- Order Items ---
with open('order_items.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['order_item_id', 'order_id', 'product_id', 'quantity', 'unit_price'])
    for i in range(1, NUM_ORDER_ITEMS + 1):
        writer.writerow([
            i,
            random.randint(1, NUM_ORDERS),
            random.randint(1, NUM_PRODUCTS),
            random.randint(1, 5),
            round(random.uniform(10, 500), 2)
        ])

# --- Payments ---
with open('payments.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['payment_id', 'order_id', 'payment_date', 'amount', 'status'])
    for i in range(1, NUM_PAYMENTS + 1):
        writer.writerow([
            i,
            i,  # one payment per order
            fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
            order_totals[i],
            random.choice(['paid', 'failed', 'refunded'])
        ])

print("Data generation complete. CSV files created.")