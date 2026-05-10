-- OrderIQ SQL Analytics Queries

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