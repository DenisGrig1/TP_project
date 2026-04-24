# Data Contract - Variant 04

**Contract version:** 0.5  
**Last updated:** 2026-04-24  
**Owner:** <Денис Григорьев>

## 1. Источник
- Название API/системы: https://archive-api.open-meteo.com/v1/archive  (open_meteo)
- Endpoint/метод: get
- Параметры запроса:
   - latitude: 51.5072
   - longitude: -0.1276
   - timezone: Europe/London
   - start_date: YYYY-MM-DD
   - end_date: YYYY-MM-DD
   - hourly:
       -    temperature_2m
       -    relative_humidity_2m
       -    precipitation
       -    wind_speed_10m

## 2. Время & часовые пояса
- `time`: ISO8601, UTC
- `date`: календарная дата, полученная в UTC

## 3. Что означает 1 строка
- normalized: 1 строка = значения температуры, влажности, осадков и скорости ветра за 1 час + id города
- mart: 1 строка = средние значения температуры, влажности и скорости ветра, сумма осадков и кол-во часов с осадками за 1 день + id города, название города, код страны, широта, долгота и часовой пояс

## 4. Наименования и единицы измерения
- snake_case
- KPI префиксы: sum_, avg_
- units фиксируются в data_dictionary.md

## 5. Схема normalized
| Поле | Тип | Nullable | Описание | Пример |
| --- | --- | --- | --- | --- |
|time|datetime64[ns]|нет|Зерно таблицы, время измерения показателей|2026-03-10 02:00:00|
|temperature_2m|float64|нет|Температура воздуха в градусах Цельсия на высоте 2 метра|11.9|
|relative_humidity_2m|float32|нет|Влажность воздуха в процентах на высоте 2 метра|85.2|
|precipitation|float64|нет|Осадки в мм|2.0|
|wind_speed_10m|float64|нет|Скорость ветра в км/ч на высоте 10 метров|16.3|
|city_id|str|нет|ID города|GB_LON|

## 6. Схема mart
| Поле | Тип | Nullable | Описание | Пример |
| --- | --- | --- | --- | --- |
|date|object|нет|Календарная дата, полученная в UTC|2026-03-10|
|avg_temperature_2m|float64|нет|Средняя температура воздуха в градусах Цельсия на высоте 2 метра за день|9.1|
|avg_relative_humidity_2m|float32|нет|Средняя влажность воздуха в процентах на высоте 2 метра за день|96.0|
|sum_precipitation|float64|нет|Сумма осадков в мм за день|0.0|
|avg_wind_speed_10m|float64|нет|Средняя скорость ветра в км/ч на высоте 10 метров за день|7.3|
|rainy_hours|int|нет|Кол-во часов с осадками за день|8|
|city_id|str|нет|ID города|GB_LON|
|city_name|str|нет|Название города|Лондон|
|country_code|str|нет|ID страны|GB|
|latitude|float64|нет|Широта, на которой находится город|51.5072|
|longitude|float64|нет|Долгота, на которой находится город|-0.1276|
|timezone|str|нет|Часовой пояс, в котором находится город|Europe/London|

## 7. Правила DQ
| Check | Layer | Level | Description | Failure condition |
|---|---|---|---|---|
| check_non_empty | normalized | FAIL | Таблица не пустая | row_count = 0 |
| check_not_null | normalized | FAIL | Временная метка time должна быть заполнена. | Содержит NULL. |
| check_unique_key | normalized | FAIL | Все комбинации time и city_id должны быть уникальны | dup_count > 0 |
| check_numeric_range(temperature_2m) | normalized | WARNING | Температура должна быть в допустимом диапазоне. | Значение < -80 или > 60. |
| check_numeric_range(relative_humidity_2m) | normalized | WARNING | Влажность должна быть в допустимом диапазоне. | Значение < 0 или > 100. |
| check_non_negative(precipitation) | normalized | WARNING | Значения осадков должны быть не меньше 0. | bad_count > 0. |

## 8. Версионирование
- 0.5 (2026-04-24): Добавлены схема mart, разделы "Наименования и единицы измерения", "Что означает 1 строка", "Время & часовые пояса"
- 0.4 (2026-04-12): Добавлен раздел "Правила DQ"
- 0.2 (2026-03-18): Добавлены раздел "Источник" и схема normalized 
- 0.1 (2026-03-10): создание Data_Contract.md
