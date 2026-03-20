"""Преобразует JSON-результат SPARQL (wikidata_export_contact.json) в Mermaid-граф.

Запуск:
  python json_to_mermaid.py

Результат: scripts/wikidata_graph.mmd
"""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent.parent
IN = ROOT / "data" / "wikidata_export_contact.json"
OUT = ROOT / "images" / "wikidata_graph.mmd"

import hashlib


def make_id(label: str) -> str:
    """Возвратить стабильный короткий идентификатор узла для Mermaid.

    Используем хеш, чтобы разные русские метки не превращались в один и тот же
    идентификатор (как было, когда все символы заменялись на '_').
    """
    key = label.strip()
    if not key:
        return "node"
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]
    # Обозначим, что это узел, и добавим часть хеша для уникальности.
    return f"n_{digest}"


def load_bindings(path: pathlib.Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("results", {}).get("bindings", [])


def get_label(field):
    if not isinstance(field, dict):
        return ""
    return field.get("value", "")


def build_mermaid(bindings) -> str:
    nodes = {}
    edges = []
    seen = set()

    for b in bindings:
        src_lbl = get_label(b.get("sourceLabel")) or get_label(b.get("source"))
        tgt_lbl = get_label(b.get("targetLabel")) or get_label(b.get("target"))
        prop_lbl = get_label(b.get("propertyLabel")) or ""

        if not src_lbl or not tgt_lbl:
            continue

        src_id = make_id(src_lbl)
        tgt_id = make_id(tgt_lbl)

        nodes[src_id] = src_lbl
        nodes[tgt_id] = tgt_lbl

        prop = prop_lbl.strip()
        if prop:
            prop = prop.replace('"', "'")
            edge = f"    {src_id} -- \"{prop}\" --> {tgt_id}"
        else:
            edge = f"    {src_id} --> {tgt_id}"

        if edge not in seen:
            seen.add(edge)
            edges.append(edge)

    lines = [
        "%%{",
        "    init: {",
        "        'theme': 'base',",
        "        'themeVariables': { 'fontSize': '18px' }",
        "    }",
        "}%%",
        "",
        "graph LR",
    ]

    # define nodes to keep labels readable
    for node_id, label in nodes.items():
        safe = label.replace('"', "'")
        lines.append(f"    {node_id}[\"{safe}\"]")

    lines.append("")
    lines.extend(edges)

    return "\n".join(lines)


def main():
    bindings = load_bindings(IN)
    if not bindings:
        print(f"Нет данных в {IN}. Сначала выполните contact.py")
        return
    mermaid = build_mermaid(bindings)
    OUT.write_text(mermaid, encoding="utf-8")
    print(f"Mermaid-граф сгенерирован: {OUT}")


if __name__ == "__main__":
    main()
