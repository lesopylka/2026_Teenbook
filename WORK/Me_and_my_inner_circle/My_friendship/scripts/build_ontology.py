from pathlib import Path
import json
from graphviz import Digraph

IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"
DATA_PATH  = Path(__file__).resolve().parent.parent / "data" / "wikidata_export.json"
IMAGES_DIR.mkdir(exist_ok=True)

with open(DATA_PATH, encoding="utf-8") as f:
    data = json.load(f)

concept_labels = [c["conceptLabel"] for c in data["concepts"] if "conceptLabel" in c]

manual_edges = [
    ("дружба",       "доверие",         "основана на"),
    ("дружба",       "привязанность",   "выражается в"),
    ("дружба",       "социальная сеть", "формирует"),
    ("дружба",       "одиночество",     "противоположность"),
    ("доверие",      "предательство",   "нарушается при"),
    ("конфликт",     "предательство",   "может привести к"),
    ("привязанность","конфликт",        "может перейти в"),
    ("одиночество",  "конфликт",        "провоцирует"),
]

all_edges = manual_edges
concept_set = set(concept_labels)
edges = [(a, b, lbl) for a, b, lbl in all_edges if a in concept_set and b in concept_set]

used = set()
for a, b, _ in edges:
    used.add(a); used.add(b)

dot = Digraph(encoding="utf-8")
dot.attr(
    rankdir="TB",
    bgcolor="white",
    fontname="Arial",
    label="Онтология: Моя дружба  ·  Раздел: Я и ближний круг",
    labelloc="t",
    fontsize="16",
    pad="0.5",
    nodesep="0.5",
    ranksep="0.7",
)
dot.attr("node",
    shape="box",
    style="rounded,filled",
    fillcolor="white",
    fontname="Arial",
    fontsize="13",
    width="1.6",
    height="0.5",
    penwidth="1.5",
    color="black",
)
dot.attr("edge",
    fontname="Arial",
    fontsize="10",
    color="#555555",
    arrowsize="0.8",
)

for label in concept_labels:
    if label in used:
        dot.node(label, label)

for a, b, lbl in edges:
    dot.edge(a, b, label=f"  {lbl}  ")

out = str(IMAGES_DIR / "ontology")
dot.render(out, format="png", cleanup=True)