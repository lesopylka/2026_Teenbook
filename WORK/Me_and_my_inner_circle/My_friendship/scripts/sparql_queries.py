import urllib.request
import urllib.parse
import json
from pathlib import Path

ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    "User-Agent": "FriendshipOntologyBot/1.0 (educational project)",
    "Accept": "application/json"
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

KNOWN_LABELS = {
    "Q136685084": "дружба",
    "Q659974":    "доверие",
    "Q223270":    "одиночество",
    "Q2166722":   "предательство",
    "Q2173366":   "привязанность",
    "Q5283178":   "социальная сеть",
    "Q180684":    "конфликт",
}

QUERY_CONCEPTS = """
SELECT DISTINCT ?concept ?conceptLabel ?description WHERE {
  VALUES ?concept {
    wd:Q136685084 wd:Q659974 wd:Q223270 wd:Q2166722
    wd:Q2173366 wd:Q5283178 wd:Q180684
  }
  OPTIONAL {
    ?concept schema:description ?description
    FILTER(LANG(?description) = "ru")
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }
}
"""

def run_query(sparql):
    params = urllib.parse.urlencode({"query": sparql, "format": "json"}).encode()
    req = urllib.request.Request(ENDPOINT, data=params, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = json.loads(r.read())["results"]["bindings"]
    print(f"Получено записей: {len(rows)}")
    return [{k: v["value"] for k, v in row.items()} for row in rows]


r1 = run_query(QUERY_CONCEPTS)

concepts_clean = []
for row in r1:
    qid = row.get("concept", "").split("/")[-1]
    concepts_clean.append({
        "concept":      row.get("concept", ""),
        "conceptLabel": KNOWN_LABELS.get(qid, row.get("conceptLabel", "")),
        "description":  row.get("description", ""),
    })


output = {
    "project": "Моя дружба — РАЗДЕЛ: Я и ближний круг",
    "source": "WikiData SPARQL endpoint",
    "concepts": concepts_clean,
}

out_path = DATA_DIR / "wikidata_export.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ Сохранено в {out_path}")