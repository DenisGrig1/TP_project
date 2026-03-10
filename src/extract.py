import requests
import yaml
import json
from datetime import datetime, timedelta

try:
    with open("variant_4.yml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
        week2_fields = {
            "variant_id": config["variant_id"],
            "source_type": config["source_type"],
            "base_url": config["api"]["base_url"],
            "method": config["api"]["method"],
            "params": config["api"]["params"]
        }
        
    print(f"Вариант: {week2_fields['variant_id']}")
    print(f"Источник: {week2_fields['source_type']}")
    print(f"URL: {week2_fields['base_url']}")
        
    try:
        r = requests.get(week2_fields["base_url"], params=week2_fields["params"], timeout=10)
        r.raise_for_status()
            
    except requests.exceptions.Timeout:
        print("Ошибка: Превышен таймаут ожидания ответа от сервера")
        exit(1)
    except requests.exceptions.ConnectionError:
        print("Ошибка: Не удалось подключиться к серверу. Проверьте интернет-соединение")
        exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP: {e}")
        exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Неизвестная ошибка при выполнении запроса: {e}")
        exit(1)
        
    print(f"Статус ответа: {r.status_code}")
        
    try:
        data = r.json()
    except json.JSONDecodeError as e:
        print(f"Ошибка разбора JSON: {e}")
        print("Полученный ответ не является корректным JSON")
        exit(1)
        
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}.json"
        
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent="\t")
    except IOError as e:
        print(f"Ошибка при сохранении файла: {e}")
        exit(1)
        
    data_size = len(json.dumps(data, ensure_ascii=False))
    print(f"Сохранено в файл: {filename}")
    print(f"Размер данных: {data_size} байт")
    print("Операция успешно завершена")
        
except FileNotFoundError:
    print("Ошибка: Файл конфигурации 'variant_4.yml' не найден")
except yaml.YAMLError as e:
    print(f"Ошибка при разборе YAML файла: {e}")
except Exception as e:
    print(f"Непредвиденная ошибка: {e}")
