# Data Contract (шаблон)

## 1. Источник
- Название API/системы: https://archive-api.open-meteo.com/v1/archive
- Endpoint/метод: get
- Параметры запроса:
   - latitude: 51.5072
   - longitude: -0.1276
   - timezone: Europe/London
   - hourly:
    - temperature_2m
    - relative_humidity_2m
    - precipitation
    - wind_speed_10m
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

