-- OrderIQ SQL Analytics Queries
-- These are sample business analysis queries based on the OrderIQ database structure.

-- Total orders
SELECT COUNT(*) AS total_orders
FROM orders;

-- Orders by status
SELECT 
    order_status,
    COUNT(*) AS total_orders
FROM orders
GROUP BY order_status;

-- Payment method analysis
SELECT 
    payment_type,
    COUNT(*) AS total_payments,
    SUM(payment_value) AS total_payment_value
FROM payments
GROUP BY payment_type;

-- Region-wise orders
SELECT 
    c.customer_state,
    COUNT(o.order_id) AS total_orders
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY total_orders DESC;

-- Late delivery analysis
SELECT 
    COUNT(*) AS late_deliveries
FROM orders
WHERE order_delivered_timestamp > order_estimated_delivery_date;

-- Average delivery time
SELECT 
    AVG(DATEDIFF(DAY, order_purchase_timestamp, order_delivered_timestamp)) AS avg_delivery_days
FROM orders
WHERE order_delivered_timestamp IS NOT NULL;