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
    wd:Q10861465    # Брат
    wd:Q595094    # Сестра
    wd:Q124674557   # Сепарация
    wd:Q180684     # Конфликт
    wd:Q378529     # Примирение
    wd:Q93190      # Развод
    wd:Q7002058    # Границы
    wd:Q82821     # Традиции
    wd:Q11024      # Общение
    wd:Q182263     # Эмпатия
    wd:Q537963     # Прощение
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
    (wd:Q1492760 wd:Q7566 wdt:P40)        # подросток → родители (имеет родителя)
    (wd:Q1492760 wd:Q10861465 wdt:P451)   # подросток → брат (имеет родственника)
    (wd:Q1492760 wd:Q595094 wdt:P451)     # подросток → сестра (имеет родственника)
    (wd:Q7566 wd:Q1492760 wdt:P40)        # родители → подросток (имеют ребёнка)
    
    # Процессы и отношения
    (wd:Q1492760 wd:Q124674557 wdt:P129)  # подросток → сепарация (связан с)
    (wd:Q124674557 wd:Q180684 wdt:P129)   # сепарация → конфликт (связан с)
    (wd:Q180684 wd:Q378529 wdt:P1382)     # конфликт → примирение (частично совпадает)
    
    # Развод и его последствия
    (wd:Q93190 wd:Q1492760 wdt:P129)      # развод → подросток (связан с)
    (wd:Q93190 wd:Q180684 wdt:P129)       # развод → конфликт (связан с)
    (wd:Q93190 wd:Q82821 wdt:P129)        # развод → традиции (связан с)
    (wd:Q93190 wd:Q7566 wdt:P129)         # развод → родители (связан с)
    
    # Эмоции и качества
    (wd:Q182263 wd:Q378529 wdt:P129)      # эмпатия → примирение (связан с)
    (wd:Q537963 wd:Q378529 wdt:P129)      # прощение → примирение (связан с)
    (wd:Q7002058 wd:Q180684 wdt:P1535)    # границы → конфликт (препятствует)
    (wd:Q11024 wd:Q378529 wdt:P129)       # общение → примирение (связан с)
    
    # Традиции
    (wd:Q82821 wd:Q7566 wdt:P129)         # традиции → родители (связан с)
    (wd:Q82821 wd:Q10861465 wdt:P129)     # традиции → брат (связан с)
    (wd:Q82821 wd:Q595094 wdt:P129)       # традиции → сестра (связан с)
    (wd:Q82821 wd:Q1492760 wdt:P129)      # традиции → подросток (связан с)
    (wd:Q82821 wd:Q378529 wdt:P129)       # традиции → примирение (связан с)
    
    # Брат/сестра взаимодействия
    (wd:Q10861465 wd:Q180684 wdt:P129)    # брат → конфликт (связан с)
    (wd:Q595094 wd:Q180684 wdt:P129)      # сестра → конфликт (связан с)
    (wd:Q10861465 wd:Q378529 wdt:P129)    # брат → примирение (связан с)
    (wd:Q595094 wd:Q378529 wdt:P129)      # сестра → примирение (связан с)
  }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }
}
"""

def run_query(query: str, retries: int = 3) -> dict:
    """Выполняет SPARQL-запрос к Wikidata с повторными попытками"""
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "family-ontology-builder/1.0"
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(
                URL,
                params={"query": query, "format": "json"},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Попытка {attempt + 1} не удалась: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Экспоненциальная задержка
            else:
                print("Все попытки исчерпаны")
                return {"head": {"vars": []}, "results": {"bindings": []}}

def add_custom_entries(data: dict) -> dict:
    """Добавляет ручные записи для понятий, отсутствующих в Wikidata"""
    custom_bindings = [
        # Просьба (отсутствует в Wikidata)
        {
            "source": {"type": "uri", "value": "http://example.org/Q9000001"},
            "sourceLabel": {"xml:lang": "ru", "type": "literal", "value": "просьба"},
            "property": {"type": "uri", "value": "http://www.wikidata.org/entity/P129"},
            "propertyLabel": {"xml:lang": "ru", "type": "literal", "value": "связан с"},
            "target": {"type": "uri", "value": "http://www.wikidata.org/entity/Q7566"},
            "targetLabel": {"xml:lang": "ru", "type": "literal", "value": "родители"}
        },
        {
            "source": {"type": "uri", "value": "http://example.org/Q9000001"},
            "sourceLabel": {"xml:lang": "ru", "type": "literal", "value": "просьба"},
            "property": {"type": "uri", "value": "http://www.wikidata.org/entity/P129"},
            "propertyLabel": {"xml:lang": "ru", "type": "literal", "value": "связан с"},
            "target": {"type": "uri", "value": "http://www.wikidata.org/entity/Q1144876"},
            "targetLabel": {"xml:lang": "ru", "type": "literal", "value": "границы"}
        },
        {
            "source": {"type": "uri", "value": "http://example.org/Q9000001"},
            "sourceLabel": {"xml:lang": "ru", "type": "literal", "value": "просьба"},
            "property": {"type": "uri", "value": "http://www.wikidata.org/entity/P129"},
            "propertyLabel": {"xml:lang": "ru", "type": "literal", "value": "связан с"},
            "target": {"type": "uri", "value": "http://www.wikidata.org/entity/Q182263"},
            "targetLabel": {"xml:lang": "ru", "type": "literal", "value": "эмпатия"}
        }
    ]
    
    data["results"]["bindings"].extend(custom_bindings)
    return data

def save_result(data: dict, output_path: str) -> None:
    """Сохраняет результат в JSON-файл"""
    path = pathlib.Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Сохранено {len(data.get('results', {}).get('bindings', []))} записей в {output_path}")

print("Запрос элементов из Wikidata...")
items_data = run_query(ITEMS_QUERY)
if items_data:
    save_result(items_data, "./data/wikidata_export.json")

print("\nЗапрос связей из Wikidata...")
contacts_data = run_query(CONTACTS_QUERY)
if contacts_data:
    # Добавляем ручные записи для "просьбы"
    contacts_data = add_custom_entries(contacts_data)
    save_result(contacts_data, "./data/wikidata_export_contact.json")

print("\nГотово!")