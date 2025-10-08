# Query Performance Analysis: EXPLAIN Before & After Index

## Purpose

The purpose of these files is to demonstrate how adding an index improves SQL query performance.
`EXPLAIN ANALYZE` shows the query execution plan, including scan types, number of rows processed, and estimated costs.

## Process

1. Run the query without any index and save the output:
   - File: outputs/explain_before_index.txt
   - Observation: Sequential scan on the orders table; high cost; many rows scanned.

2. Create an index on the column customer_id in the orders table:
```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

3. Run the query again and save the output:
   - File: outputs/explain_after_index.txt
   - Observation: Index scan used; drastically fewer rows scanned; lower cost.

## Observations

| Metric                  | Before Index       | After Index       |
|-------------------------|-----------------|-----------------|
| Scan type               | Seq Scan        | Index Scan      |
| Rows scanned            | 100,000         | 200             |
| Estimated cost          | 1500.25         | 15.50           |

## Conclusion

Adding an index on customer_id significantly reduced the number of scanned rows and lowered query execution cost, improving performance.
