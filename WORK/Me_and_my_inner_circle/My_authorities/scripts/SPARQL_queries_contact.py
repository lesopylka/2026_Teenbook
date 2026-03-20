import json
import pathlib
import requests

QUERY = """
SELECT DISTINCT ?source ?sourceLabel ?property ?propertyLabel ?target ?targetLabel WHERE {
  VALUES ?source {
    wd:Q131774
    wd:Q37226
    wd:Q48282
    wd:Q11024
    wd:Q3220391
    wd:Q3914
    wd:Q8434
    wd:Q30849
  }

  VALUES ?directProp {
    wdt:P31
    wdt:P279
    wdt:P361
    wdt:P1269
    wdt:P1552
    wdt:P1889
  }

  ?source ?directProp ?target .
  FILTER(isIRI(?target))

  ?property wikibase:directClaim ?directProp .

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en"
  }
}
LIMIT 200
"""

URL = "https://query.wikidata.org/sparql"


def run_query(query: str) -> dict:
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "teenbook-authorities-project/1.0 (educational project)"
    }

    response = requests.get(
        URL,
        params={"query": query, "format": "json"},
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def save_result(data: dict, output_path: pathlib.Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    script_dir = pathlib.Path(__file__).resolve().parent
    output_path = script_dir.parent / "data" / "wikidata_export_contact.json"

    data = run_query(QUERY)
    save_result(data, output_path)

    print(f"Готово: результат сохранён в {output_path}")


if __name__ == "__main__":
    main()