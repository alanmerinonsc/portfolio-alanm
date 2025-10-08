-- tables for e-commerce db
CREATE TABLE customers (
  customer_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE products (
  product_id SERIAL PRIMARY KEY,
  sku TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  price NUMERIC(10,2) NOT NULL
);

CREATE TABLE orders (
  order_id SERIAL PRIMARY KEY,
  customer_id INT NOT NULL REFERENCES customers(customer_id),
  order_date DATE NOT NULL,
  total_amount NUMERIC(10,2) NOT NULL,
  status TEXT NOT NULL
);

CREATE TABLE order_items (
  order_item_id SERIAL PRIMARY KEY,
  order_id INT NOT NULL REFERENCES orders(order_id),
  product_id INT NOT NULL REFERENCES products(product_id),
  quantity INT NOT NULL,
  unit_price NUMERIC(10,2) NOT NULL
);

CREATE TABLE payments (
  payment_id SERIAL PRIMARY KEY,
  order_id INT NOT NULL REFERENCES orders(order_id),
  payment_date TIMESTAMP,
  amount NUMERIC(10,2),
  status TEXT
);
-- indexes
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
