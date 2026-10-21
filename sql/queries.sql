-- PesaPap Capstone SQL Queries

-- Query 1: Acquisition channel performance using JOIN and GROUP BY
SELECT
    u.acquisition_channel,
    COUNT(DISTINCT u.user_id) AS customers,
    COUNT(t.txn_id) AS transactions,
    ROUND(SUM(t.amount), 2) AS total_value,
    ROUND(AVG(t.amount), 2) AS average_transaction_value
FROM users AS u
LEFT JOIN transactions AS t
    ON u.user_id = t.user_id
GROUP BY u.acquisition_channel
ORDER BY total_value DESC;

-- Query 2: Product performance using GROUP BY
SELECT
    product,
    COUNT(txn_id) AS transactions,
    ROUND(SUM(amount), 2) AS total_value,
    ROUND(AVG(amount), 2) AS average_transaction_value
FROM transactions
GROUP BY product
ORDER BY total_value DESC;

-- Query 3: Monthly trend using CTE, LAG and running SUM window functions
WITH monthly AS (
    SELECT
        strftime('%Y-%m', txn_date) AS month,
        COUNT(txn_id) AS transactions,
        SUM(amount) AS monthly_value
    FROM transactions
    GROUP BY strftime('%Y-%m', txn_date)
),
with_previous AS (
    SELECT
        month,
        transactions,
        monthly_value,
        LAG(monthly_value) OVER (
            ORDER BY month
        ) AS previous_value,
        SUM(monthly_value) OVER (
            ORDER BY month
        ) AS running_total
    FROM monthly
)
SELECT
    month,
    transactions,
    ROUND(monthly_value, 2) AS monthly_value,
    ROUND(running_total, 2) AS running_total,
    ROUND(
        (
            monthly_value - previous_value
        ) * 100.0 / previous_value,
        2
    ) AS mom_growth_pct
FROM with_previous
ORDER BY month;

-- Query 4: County performance using JOIN and GROUP BY
SELECT
    u.county,
    COUNT(DISTINCT u.user_id) AS customers,
    COUNT(t.txn_id) AS transactions,
    ROUND(SUM(t.amount), 2) AS total_value,
    ROUND(
        SUM(t.amount) / COUNT(DISTINCT u.user_id),
        2
    ) AS value_per_customer
FROM users AS u
LEFT JOIN transactions AS t
    ON u.user_id = t.user_id
GROUP BY u.county
ORDER BY total_value DESC;

-- Query 5: Products above average transaction threshold using HAVING
SELECT
    product,
    COUNT(txn_id) AS transactions,
    ROUND(AVG(amount), 2) AS average_transaction_value
FROM transactions
GROUP BY product
HAVING AVG(amount) > 1550
ORDER BY average_transaction_value DESC;

-- Query 6: Top customer value using RANK window function
WITH customer_value AS (
    SELECT
        u.user_id,
        u.acquisition_channel,
        u.county,
        COUNT(t.txn_id) AS transactions,
        SUM(t.amount) AS total_value
    FROM users AS u
    JOIN transactions AS t
        ON u.user_id = t.user_id
    GROUP BY
        u.user_id,
        u.acquisition_channel,
        u.county
),
ranked AS (
    SELECT
        *,
        RANK() OVER (
            ORDER BY total_value DESC
        ) AS value_rank
    FROM customer_value
)
SELECT *
FROM ranked
WHERE value_rank <= 20
ORDER BY value_rank;
