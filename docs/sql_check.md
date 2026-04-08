-- 1. Таблица не пуста

SELECT COUNT(*) AS row_count
FROM mart_daily_2026-03-19_17-13-07;

-- 2. Диапазон дат

SELECT MIN(date) AS min_date,
       MAX(date) AS max_date
FROM mart_daily_2026-03-19_17-13-07;

-- 3. NULL в ключевых колонках

SELECT
    SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END) AS null_date,
    SUM(CASE WHEN city_id IS NULL THEN 1 ELSE 0 END) AS null_city_id
FROM mart_daily_2026-03-19_17-13-07;

-- 4. Дубли по бизнес-ключу

SELECT date, city_id, COUNT(*) AS cnt
FROM mart_daily_2026-03-19_17-13-07
GROUP BY date, city_id
HAVING COUNT(*) > 1;

-- 5. KPI-проверка

SELECT city_id,
       SUM(revenue) AS total_revenue,
       AVG(conversion_rate) AS avg_conversion
FROM mart_daily_2026-03-19_17-13-07
GROUP BY city_id;
