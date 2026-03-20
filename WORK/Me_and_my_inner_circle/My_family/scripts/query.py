import json
import pathlib
import requests
import time

URL = "https://query.wikidata.org/sparql"

# Запрос для получения элементов
ITEMS_QUERY = """
SELECT ?item ?itemLabel ?description WHERE {
  VALUES ?item {
    wd:Q1492760    # Подросток
    wd:Q7566       # Родители
    wd:Q10861465   # Брат
    wd:Q595094     # Сестра
    wd:Q124674557  # Сепарация
    wd:Q180684     # Конфликт
    wd:Q378529     # Примирение
    wd:Q93190      # Развод
    wd:Q7002058    # Границы
    wd:Q82821      # Традиции
    wd:Q11024      # Общение
    wd:Q182263     # Эмпатия
    wd:Q537963     # Прощение
    wd:Q22445448   # Просьба
  }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }
  
  OPTIONAL {
    ?item schema:description ?description
    FILTER(LANG(?description) = "ru")
  }
}
"""

# Запрос для получения связей
CONTACTS_QUERY = """
SELECT ?source ?sourceLabel ?property ?propertyLabel ?target ?targetLabel WHERE {
  VALUES (?source ?target ?property) {
    # Семейные связи
    (wd:Q1492760 wd:Q7566 wdt:P40)
    (wd:Q1492760 wd:Q10861465 wdt:P451)
    (wd:Q1492760 wd:Q595094 wdt:P451)
    (wd:Q7566 wd:Q1492760 wdt:P40)
    
    # Процессы и отношения
    (wd:Q1492760 wd:Q124674557 wdt:P129)
    (wd:Q124674557 wd:Q180684 wdt:P129)
    (wd:Q180684 wd:Q378529 wdt:P1382)
    
    # Развод и его последствия
    (wd:Q93190 wd:Q1492760 wdt:P129)
    (wd:Q93190 wd:Q180684 wdt:P129)
    (wd:Q93190 wd:Q82821 wdt:P129)
    (wd:Q93190 wd:Q7566 wdt:P129)
    
    # Эмоции и качества
    (wd:Q182263 wd:Q378529 wdt:P129)
    (wd:Q537963 wd:Q378529 wdt:P129)
    (wd:Q7002058 wd:Q180684 wdt:P1535)
    (wd:Q11024 wd:Q378529 wdt:P129)
    
    # Традиции
    (wd:Q82821 wd:Q7566 wdt:P129)
    (wd:Q82821 wd:Q10861465 wdt:P129)
    (wd:Q82821 wd:Q595094 wdt:P129)
    (wd:Q82821 wd:Q1492760 wdt:P129)
    (wd:Q82821 wd:Q378529 wdt:P129)
    
    # Брат/сестра взаимодействия
    (wd:Q10861465 wd:Q180684 wdt:P129)
    (wd:Q595094 wd:Q180684 wdt:P129)
    (wd:Q10861465 wd:Q378529 wdt:P129)
    (wd:Q595094 wd:Q378529 wdt:P129)
    
    # Просьба и её связи 
    (wd:Q22445448 wd:Q7566 wdt:P129)
    (wd:Q22445448 wd:Q7002058 wdt:P129)
    (wd:Q22445448 wd:Q11024 wdt:P129)
    (wd:Q22445448 wd:Q378529 wdt:P129)
    (wd:Q22445448 wd:Q182263 wdt:P129)
    (wd:Q180684 wd:Q22445448 wdt:P129)
  }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }
}
"""

def run_query(query: str, retries: int = 3) -> dict:
    """Выполняет SPARQL-запрос к Wikidata с повторными попытками"""
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "teenbook-authorities-project/1.0 (educational project)"
    }
    
    for attempt in range(retries):
        try:
            print(f"Выполнение запроса (попытка {attempt + 1})...")
            response = requests.get(
                URL,
                params={"query": query, "format": "json"},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            print("Запрос успешно выполнен")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"Ожидание {wait} секунд...")
                time.sleep(wait)
            else:
                print("Все попытки исчерпаны")
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга ответа: {e}")
            break
    
    return {"head": {"vars": []}, "results": {"bindings": []}}

def save_result(data: dict, output_path: str) -> None:
    """Сохраняет результат в JSON-файл"""
    path = pathlib.Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    count = len(data.get('results', {}).get('bindings', []))
    print(f"Сохранено {count} записей в {output_path}")

items_data = run_query(ITEMS_QUERY)
if items_data and "results" in items_data:
    save_result(items_data, "./data/wikidata_export.json")

print("\n=== ЗАПРОС СВЯЗЕЙ ИЗ WIKIDATA ===\n")
contacts_data = run_query(CONTACTS_QUERY)
if contacts_data and "results" in contacts_data:
    save_result(contacts_data, "./data/wikidata_export_contact.json")

print("\n✅ Готово! Все файлы сохранены в ./data/")