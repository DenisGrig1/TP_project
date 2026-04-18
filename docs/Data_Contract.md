# Data Contract (шаблон)

## 1. Источник
- Название API/системы: https://archive-api.open-meteo.com/v1/archive  (open_meteo)
- Endpoint/метод: get
- Параметры запроса:
   - latitude: 51.5072
   - longitude: -0.1276
   - timezone: Europe/London
   - hourly:
       -    temperature_2m
       -    relative_humidity_2m
       -    precipitation
       -    wind_speed_10m
- Частота обновления: каждый час

## 2. Владение и ответственность
- Owner (кто отвечает за данные):
- Consumer (кто использует):
- SLA/SLO (по желанию):

## 3. Схема (normalized)
Опишите таблицу после приведения JSON к табличному виду.

| Поле | Тип | Nullable | Описание | Пример |
| --- | --- | --- | --- | --- |
|time|datetime64[ns]|нет|Зерно таблицы, время измерения показателей|2026-03-10 02:00:00|
|temperature_2m|float64|нет|Температура воздуха в градусах Цельсия на высоте 2 метра|9.1|
|relative_humidity_2m|float32|нет|Влажность воздуха в процентах на высоте 2 метра|96.0|
|precipitation|float64|нет|Кол-во осадков в мм|0.0|
|wind_speed_10m|float64|нет|Скорость ветра в км/ч на высоте 10 метров|7.3|

## 4. Допущения и единицы измерения
- Температура: °C или K?
- Время: UTC или локальное?
- Денежные единицы:

## 5. Правила качества
- Uniqueness:
- Completeness:
- Validity:
- Freshness:
- Consistency:

## 6. Версионирование
- Версия контракта:
- Как фиксируете изменения:

## 7. DQ Rules

| Check | Layer | Level | Description | Failure condition |
|---|---|---|---|---|
| check_non_empty | normalized | FAIL | Таблица не пустая | row_count = 0 |
| check_not_null | normalized | FAIL | Временная метка time должна быть заполнена. | Содержит NULL. |
| check_unique_key | normalized | FAIL | Все комбинации time и city_id должны быть уникальны | dup_count > 0 |
| check_numeric_range(temperature_2m) | normalized | WARNING | Температура должна быть в допустимом диапазоне. | Значение < -80 или > 60. |
| check_numeric_range(relative_humidity_2m) | normalized | WARNING | Влажность должна быть в допустимом диапазоне. | Значение < 0 или > 100. |
| check_non_negative(precipitation) | normalized | WARNING | Значения осадков должны быть не меньше 0. | bad_count > 0. |
