# Data Dictionary — mart_daily

| column | business meaning | unit | notes/example |
|---|---|---|---|
|date|Календарная дата агрегации (день)|YYYY-MM-DD|агрегировано в UTC|
|temperature_2m|Средняя температура воздуха на высоте 2 метра за день|°C|mean(temperature_2m)|
|relative_humidity_2m|Средняя влажность воздуха на высоте 2 метра за день|%|mean(relative_humidity_2m)|
|precipitation|Сумма осадков за день|mm|sum(precipitation)|
|wind_speed_10m|Средняя скорость ветра на высоте 10 метров за день|km/h|mean(wind_speed_10m)|
|rainy_hours|Кол-во часов с осадками за день|rainy_hours/date|rainy_hour = precipitation > 0, sum(rainy_hour)|
|city_id|ID города|-|Из конфига variant_04.yml|
|city_name|Человекочитаемое название города|-|Из справочника cities.csv|
|country_code|ID страны|-|Из справочника cities.csv|
|latitude|Широта, на которой находится город|Число|Из справочника cities.csv|
|longitude|Долгота, на которой находится город|Число|Из справочника cities.csv|
|timezone|Часовой пояс, в котором находится город|-|Из справочника cities.csv|
