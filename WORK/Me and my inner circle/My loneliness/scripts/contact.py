import json
import pathlib
import requests

QUERY = """
SELECT ?source ?sourceLabel ?property ?propertyLabel ?target ?targetLabel WHERE {
  VALUES ?source {
    wd:Q223270 
    wd:Q6010868 
    wd:Q19192960  
    wd:Q19192957 
    wd:Q908826 
    wd:Q1910993 
    wd:Q1778765 
    wd:Q1096367  
    wd:Q309406 
    wd:Q545825   
    wd:Q4340209 
    wd:Q545365 
  }

  VALUES ?target {
    wd:Q1910993 
    wd:Q1778765 
    wd:Q1096367  
    wd:Q309406 
    wd:Q545825   
    wd:Q4340209 
    wd:Q545365 
    wd:Q223270  
    wd:Q6010868 
    wd:Q19192960  
    wd:Q19192957 
    wd:Q908826 
  }

  ?source ?directProp ?target .
  ?property wikibase:directClaim ?directProp .

  FILTER(?source != ?target)

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en" .
  }
}
"""

URL = "https://query.wikidata.org/sparql"


def run_query(query: str) -> dict:
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "school-relations-project/1.0 (educational project)"
    }
    response = requests.get(
        URL,
        params={"query": query, "format": "json"},
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def save_result(data: dict, output_path: str) -> None:
    path = pathlib.Path(__file__).parent.parent / output_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Результат {path}")

def main():
    data = run_query(QUERY)
    save_result(data, "data/wikidata_export_contact.json")
    print("Готово: результат сохранён в ../data/wikidata_export_contact.json")


if __name__ == "__main__":
    main()