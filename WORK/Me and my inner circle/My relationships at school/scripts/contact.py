import json
import pathlib
import requests

QUERY = """
SELECT ?source ?sourceLabel ?property ?propertyLabel ?target ?targetLabel WHERE {
  VALUES ?source {
    wd:Q37226
    wd:Q48282
    wd:Q159334
    wd:Q491
    wd:Q240126
    wd:Q180684
    wd:Q11024
  }

  VALUES ?target {
    wd:Q37226
    wd:Q48282
    wd:Q159334
    wd:Q491
    wd:Q240126
    wd:Q180684
    wd:Q11024
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
    path = pathlib.Path(output_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    data = run_query(QUERY)
    save_result(data, "../data/wikidata_export_contact.json")
    print("Готово: результат сохранён в ../data/wikidata_export_contact.json")


if __name__ == "__main__":
    main()