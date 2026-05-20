## 1. Таблица не пуста

```sql
SELECT COUNT(*) AS row_count
FROM mart_sql;
```

## 2. Диапазон дат

```sql
SELECT MIN(date) AS min_date,
       MAX(date) AS max_date
FROM mart_sql;
```

## 3. NULL в ключевых колонках

```sql
SELECT
    SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END) AS null_date,
    SUM(CASE WHEN city_id IS NULL THEN 1 ELSE 0 END) AS null_city_id
FROM mart_sql;
```

## 4. Дубли по бизнес-ключу

```sql
SELECT date, city_id, COUNT(*) AS cnt
FROM mart_sql
GROUP BY date, city_id
HAVING COUNT(*) > 1;
```

## 5. KPI-проверка

```sql
SELECT city_id,
       SUM(revenue) AS total_revenue,
       AVG(conversion_rate) AS avg_conversion
FROM mart_sql
GROUP BY city_id;
```
