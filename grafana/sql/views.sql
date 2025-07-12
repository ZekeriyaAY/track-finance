-- Grafana Database Views for Track Finance
-- This file contains all view definitions used by Grafana dashboards

-- Drop existing views
DROP VIEW IF EXISTS grafana_monthly_summary CASCADE;
DROP VIEW IF EXISTS grafana_category_trends CASCADE;
DROP VIEW IF EXISTS grafana_investment_performance CASCADE;
DROP VIEW IF EXISTS grafana_cashflow_analysis CASCADE;

-- 1. Monthly Summary View
CREATE VIEW grafana_monthly_summary AS
SELECT DATE_TRUNC('month', date) as month,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_expenses,
    SUM(amount) as net_cashflow,
    COUNT(*) as transaction_count
FROM cashflow_transaction 
GROUP BY DATE_TRUNC('month', date) 
ORDER BY month;

-- 2. Category Trends View
CREATE VIEW grafana_category_trends AS
SELECT c.name as category_name,
    DATE_TRUNC('month', cf.date) as month,
    SUM(CASE WHEN cf.amount < 0 THEN ABS(cf.amount) ELSE 0 END) as expenses,
    SUM(CASE WHEN cf.amount > 0 THEN cf.amount ELSE 0 END) as income,
    COUNT(*) as transaction_count
FROM cashflow_transaction cf 
JOIN category c ON cf.category_id = c.id
GROUP BY c.name, DATE_TRUNC('month', cf.date) 
ORDER BY month, category_name;

-- 3. Investment Performance View
CREATE VIEW grafana_investment_performance AS
SELECT it.name as investment_type,
    i.transaction_date, i.transaction_type, i.price, i.quantity, i.total_amount,
    i.description, i.created_at
FROM investment_transaction i 
JOIN investment_type it ON i.investment_type_id = it.id
ORDER BY i.transaction_date DESC;

-- 4. Cashflow Analysis View
CREATE VIEW grafana_cashflow_analysis AS
SELECT cf.id, cf.date, cf.amount, cf.description, c.name as category_name,
    CASE WHEN cf.amount > 0 THEN 'Income' ELSE 'Expense' END as transaction_type,
    ABS(cf.amount) as absolute_amount,
    DATE_PART('year', cf.date) as year, 
    DATE_PART('month', cf.date) as month,
    DATE_PART('day', cf.date) as day, 
    TO_CHAR(cf.date, 'Day') as day_of_week
FROM cashflow_transaction cf 
JOIN category c ON cf.category_id = c.id 
ORDER BY cf.date DESC;
