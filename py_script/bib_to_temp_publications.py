#!/usr/bin/env python3
"""Convert py_script/candidate.bib into temporary publication JSON files."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "py_script" / "candidate.bib"
DEFAULT_OUTPUT = ROOT / "py_script" / "temp-pub-raw"


@dataclass
class BibEntry:
    entry_type: str
    key: str
    fields: dict[str, str]


def strip_outer_braces(value: str) -> str:
    value = value.strip()
    while len(value) >= 2 and value[0] == "{" and value[-1] == "}":
        depth = 0
        balanced = True
        for index, char in enumerate(value):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0 and index != len(value) - 1:
                    balanced = False
                    break
        if not balanced:
            break
        value = value[1:-1].strip()
    return value


def clean_text(value: str) -> str:
    value = strip_outer_braces(value)
    value = value.replace("\\&", "&")
    value = value.replace("\\_", "_")
    value = value.replace("\\%", "%")
    value = value.replace("\\#", "#")
    value = value.replace("\\$", "$")
    value = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})", r"\1", value)
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def split_top_level_fields(body: str) -> list[str]:
    fields = []
    start = 0
    brace_depth = 0
    quote_open = False

    for index, char in enumerate(body):
        if char == '"' and (index == 0 or body[index - 1] != "\\"):
            quote_open = not quote_open
        elif not quote_open:
            if char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
            elif char == "," and brace_depth == 0:
                part = body[start:index].strip()
                if part:
                    fields.append(part)
                start = index + 1

    tail = body[start:].strip()
    if tail:
        fields.append(tail)
    return fields


def parse_field(part: str) -> tuple[str, str] | None:
    match = re.match(r"\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*(.+?)\s*$", part, re.S)
    if not match:
        return None
    key = match.group(1).lower()
    value = match.group(2).strip().rstrip(",").strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    value = clean_text(value)
    return key, value


def find_entry_end(text: str, start: int) -> int:
    depth = 0
    quote_open = False
    for index in range(start, len(text)):
        char = text[index]
        if char == '"' and (index == 0 or text[index - 1] != "\\"):
            quote_open = not quote_open
        elif not quote_open:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return index + 1
    raise ValueError("BibTeX entry braces are not balanced.")


def parse_bibtex(text: str) -> list[BibEntry]:
    text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("%"))
    entries: list[BibEntry] = []
    pos = 0
    while True:
        match = re.search(r"@([A-Za-z]+)\s*\{", text[pos:])
        if not match:
            break
        entry_type = match.group(1).lower()
        open_brace = pos + match.end() - 1
        end = find_entry_end(text, open_brace)
        content = text[open_brace + 1 : end - 1]
        key_part, _, field_body = content.partition(",")
        key = key_part.strip()
        fields = {}
        for part in split_top_level_fields(field_body):
            parsed = parse_field(part)
            if parsed:
                fields[parsed[0]] = parsed[1]
        entries.append(BibEntry(entry_type=entry_type, key=key, fields=fields))
        pos = end
    return entries


def normalize_author(author: str) -> str:
    author = clean_text(author)
    if "," in author:
        parts = [part.strip() for part in author.split(",") if part.strip()]
        if len(parts) >= 2:
            return f"{parts[1]} {parts[0]}".strip()
    return author


def normalize_authors(value: str) -> str:
    authors = [normalize_author(author) for author in re.split(r"\s+and\s+", value) if author.strip()]
    return ", ".join(authors)


def publication_type(entry: BibEntry) -> str:
    if entry.entry_type in {"inproceedings", "conference", "proceedings"}:
        return "conference"
    if entry.entry_type in {"article", "periodical"}:
        return "journal"
    fields = entry.fields
    if fields.get("booktitle"):
        return "conference"
    return "journal"


def publication_venue(entry: BibEntry) -> str:
    fields = entry.fields
    if publication_type(entry) == "conference":
        return fields.get("booktitle") or fields.get("journal") or fields.get("publisher") or ""
    return fields.get("journal") or fields.get("booktitle") or fields.get("publisher") or ""


def paper_link(fields: dict[str, str]) -> str:
    for key in ("url", "html", "pdf"):
        if fields.get(key):
            return fields[key]
    doi = fields.get("doi", "").strip()
    if doi:
        doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.I)
        return f"https://doi.org/{doi}"
    return ""


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")[:90] or "publication"


def unique_slug(base: str, used: set[str]) -> str:
    slug = base
    counter = 2
    while slug in used:
        slug = f"{base}-{counter}"
        counter += 1
    used.add(slug)
    return slug


def entry_to_publication(entry: BibEntry, order: int) -> dict[str, object]:
    fields = entry.fields
    year_text = fields.get("year", "")
    year_match = re.search(r"\d{4}", year_text)
    if not year_match:
        raise ValueError(f"Entry {entry.key} is missing a valid year.")

    title = fields.get("title", "").strip()
    if not title:
        raise ValueError(f"Entry {entry.key} is missing title.")

    authors = fields.get("author", "").strip()
    if not authors:
        raise ValueError(f"Entry {entry.key} is missing author.")

    return {
        "title": title,
        "authors": normalize_authors(authors),
        "year": int(year_match.group(0)),
        "type": publication_type(entry),
        "venue": publication_venue(entry),
        "paper": paper_link(fields),
        "code": "",
        "order": order,
    }


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_candidate_json(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    for path in output_dir.glob("[0-9][0-9][0-9][0-9]/*/*.json"):
        path.unlink()
    for directory in sorted(output_dir.glob("[0-9][0-9][0-9][0-9]/*"), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    for directory in sorted(output_dir.glob("[0-9][0-9][0-9][0-9]"), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()


def convert_bib(input_path: Path, output_dir: Path, clean: bool, target_year: int | None) -> int:
    if not input_path.exists():
        raise FileNotFoundError(f"Cannot find BibTeX file: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    if clean:
        clean_candidate_json(output_dir)

    entries = parse_bibtex(input_path.read_text(encoding="utf-8"))
    if not entries:
        raise ValueError(f"No BibTeX entries found in {input_path}")

    order_by_bucket: dict[tuple[int, str], int] = {}
    used_by_bucket: dict[tuple[int, str], set[str]] = {}
    count = 0

    for entry in entries:
        bucket_type = publication_type(entry)
        year_text = entry.fields.get("year", "")
        year_match = re.search(r"\d{4}", year_text)
        if not year_match:
            raise ValueError(f"Entry {entry.key} is missing a valid year.")
        year = int(year_match.group(0))
        if target_year is not None and year != target_year:
            continue

        bucket = (year, bucket_type)
        order_by_bucket[bucket] = order_by_bucket.get(bucket, 0) + 1

        publication = entry_to_publication(entry, order_by_bucket[bucket])
        used = used_by_bucket.setdefault(bucket, set())
        slug = unique_slug(slugify(str(publication["title"])), used)
        write_json(output_dir / str(year) / bucket_type / f"{slug}.json", publication)
        count += 1

    if target_year is not None and count == 0:
        raise ValueError(f"No BibTeX entries found for year {target_year}.")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="把 py_script/candidate.bib 转成临时论文 JSON。")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="BibTeX 输入文件。")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="临时 JSON 输出目录。")
    parser.add_argument("--year", type=int, help="只转换指定年份的论文。")
    parser.add_argument("--no-clean", action="store_true", help="不清空已有临时输出目录。")
    args = parser.parse_args()

    try:
        count = convert_bib(args.input, args.output, clean=not args.no_clean, target_year=args.year)
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))
    print(f"已从 {args.input} 转换 {count} 篇论文到 {args.output}")


if __name__ == "__main__":
    main()
