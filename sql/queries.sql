-- =========================================================
-- PesaPap Capstone SQL Analysis
-- =========================================================
-- These queries answer key business questions about customer
-- acquisition, product performance, transaction trends,
-- county performance and customer value.
--
-- Required SQL features demonstrated:
-- 1. JOIN
-- 2. GROUP BY
-- 3. GROUP BY with HAVING
-- 4. Window functions
-- 5. CTEs
-- =========================================================


-- =========================================================
-- Query 1: Which acquisition channels generate the most value?
-- Requirement demonstrated: JOIN + GROUP BY
-- =========================================================
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


-- =========================================================
-- Query 2: Which products generate the most transaction value?
-- Requirement demonstrated: GROUP BY
-- =========================================================
SELECT
    product,
    COUNT(txn_id) AS transactions,
    ROUND(SUM(amount), 2) AS total_value,
    ROUND(AVG(amount), 2) AS average_transaction_value
FROM transactions
GROUP BY product
ORDER BY total_value DESC;


-- =========================================================
-- Query 3: How does transaction value change by month?
-- Requirement demonstrated:
-- CTE + LAG window function + running SUM window function
-- =========================================================
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


-- =========================================================
-- Query 4: Which counties generate the most customer value?
-- Requirement demonstrated: JOIN + GROUP BY
-- =========================================================
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


-- =========================================================
-- Query 5: Which products have above-threshold average value?
-- Requirement demonstrated: GROUP BY with HAVING
-- =========================================================
SELECT
    product,
    COUNT(txn_id) AS transactions,
    ROUND(AVG(amount), 2) AS average_transaction_value
FROM transactions
GROUP BY product
HAVING AVG(amount) > 1550
ORDER BY average_transaction_value DESC;


-- =========================================================
-- Query 6: Who are the highest-value customers?
-- Requirement demonstrated:
-- JOIN + GROUP BY + RANK window function
-- =========================================================
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
