# Data Contract (шаблон)

## 1. Источник
- Название API/системы: https://archive-api.open-meteo.com/v1/archive
- Endpoint/метод: get
- Параметры запроса:
   1. latitude: 51.5072
   2. longitude: -0.1276
   3. timezone: Europe/London
   4. hourly:
    4.1. temperature_2m
    4.2. relative_humidity_2m
    4.3. precipitation
    4.4. wind_speed_10m
- Частота обновления: каждый час

## 2. Владение и ответственность
- Owner (кто отвечает за данные):
- Consumer (кто использует):
- SLA/SLO (по желанию):

## 3. Схема (normalized)
Опишите таблицу после приведения JSON к табличному виду.

| Поле | Тип | Nullable | Описание | Пример |
|---|---|---|---|---|
| | | | | |

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

