# -*- coding: utf-8 -*-

import json
import os
import re
from pathlib import Path


HEADER_PATTERN = re.compile(r'^\s{0,3}#{1,6}\s')
MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
INLINE_CODE_PATTERN = re.compile(r'`[^`\n]+`')
CODE_BLOCK_PATTERN = re.compile(r'```.*?```', re.DOTALL)


def compile_phrase_pattern(phrase: str) -> re.Pattern:
    return re.compile(
        rf'(?<![\w/])({re.escape(phrase)})(?![\w])',
        flags=re.IGNORECASE | re.UNICODE
    )


def load_link_targets(json_path: Path) -> list[dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    targets = []
    for item in data.get("targets", []):
        concept = item["concept"].strip()
        file_path = item["file"].strip()

        aliases = set()
        aliases.add(concept)

        for alias in item.get("aliases", []):
            alias = alias.strip()
            if alias:
                aliases.add(alias)

        targets.append({
            "concept": concept,
            "file": file_path,
            "aliases": sorted(aliases, key=len, reverse=True),
        })

    return targets


def protect_fragments(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}

    def protect(pattern: re.Pattern, source: str, prefix: str) -> str:
        def repl(match: re.Match) -> str:
            key = f"@@{prefix}_{len(placeholders)}@@"
            placeholders[key] = match.group(0)
            return key
        return pattern.sub(repl, source)

    text = protect(CODE_BLOCK_PATTERN, text, "CODEBLOCK")
    text = protect(INLINE_CODE_PATTERN, text, "INLINECODE")
    text = protect(MARKDOWN_LINK_PATTERN, text, "MDLINK")
    return text, placeholders


def restore_fragments(text: str, placeholders: dict[str, str]) -> str:
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def make_relative_link(from_md: Path, to_md: Path) -> str:
    return os.path.relpath(to_md, start=from_md.parent).replace("\\", "/")


def process_markdown_file(md_path: Path, repo_root: Path, link_targets: list[dict]) -> bool:
    original_text = md_path.read_text(encoding="utf-8")
    protected_text, placeholders = protect_fragments(original_text)

    lines = protected_text.splitlines()
    updated_lines = []

    linked_concepts = set()
    changed = False
    current_abs = md_path.resolve()

    for line in lines:
        if HEADER_PATTERN.match(line):
            updated_lines.append(line)
            continue

        updated_line = line

        for target in link_targets:
            concept = target["concept"]

            if concept in linked_concepts:
                continue

            target_abs = (repo_root / target["file"]).resolve()

            if not target_abs.exists():
                continue

            if target_abs == current_abs:
                continue

            rel_link = make_relative_link(md_path, target_abs)

            for alias in target["aliases"]:
                pattern = compile_phrase_pattern(alias)
                match = pattern.search(updated_line)

                if not match:
                    continue

                found_text = match.group(1)
                replacement = f"[{found_text}]({rel_link})"
                updated_line = pattern.sub(replacement, updated_line, count=1)

                print(f"{md_path.relative_to(repo_root)}: '{found_text}' -> {rel_link}")

                linked_concepts.add(concept)
                changed = True
                break

        updated_lines.append(updated_line)

    result_text = "\n".join(updated_lines)
    result_text = restore_fragments(result_text, placeholders)

    if result_text != original_text:
        md_path.write_text(result_text, encoding="utf-8")
        return True

    return False


def main():
    script_path = Path(__file__).resolve()

    repo_root = None
    for parent in [script_path.parent, *script_path.parents]:
        if (parent / "WORK").exists() and (parent / "WEB").exists():
            repo_root = parent
            break

    if repo_root is None:
        raise RuntimeError("Не удалось найти корень репозитория.")

    link_targets_path = repo_root / "WORK" / "Me_and_my_inner_circle" / "link_targets.json"
    if not link_targets_path.exists():
        raise FileNotFoundError(f"Не найден файл: {link_targets_path}")

    section_root = repo_root / "WEB" / "Me_and_my_inner_circle"
    if not section_root.exists():
        raise FileNotFoundError(f"Не найдена папка раздела: {section_root}")

    link_targets = load_link_targets(link_targets_path)

    md_files = sorted(section_root.rglob("*.md"))
    if not md_files:
        print("Markdown-файлы не найдены.")
        return

    changed_count = 0

    for md_file in md_files:
        print(f"\nОбработка: {md_file.relative_to(repo_root)}")
        try:
            if process_markdown_file(md_file, repo_root, link_targets):
                print("  -> файл обновлен")
                changed_count += 1
            else:
                print("  -> без изменений")
        except Exception as e:
            print(f"  -> ошибка: {e}")

    print(f"\nГотово. Обработано файлов: {len(md_files)}, изменено: {changed_count}")


if __name__ == "__main__":
    main()