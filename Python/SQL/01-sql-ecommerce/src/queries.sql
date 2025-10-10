-- monthly revenue
SELECT date_trunc('month', order_date) AS month, SUM(total_amount) AS revenue
FROM orders
GROUP BY month ORDER BY month;

-- top 5 customers
SELECT c.customer_id, c.name, SUM(o.total_amount) total_spent
FROM customers c JOIN orders o USING(customer_id)
GROUP BY c.customer_id,c.name ORDER BY total_spent DESC LIMIT 5;

-- products never purchased
SELECT p.* FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.product_id IS NULL;
