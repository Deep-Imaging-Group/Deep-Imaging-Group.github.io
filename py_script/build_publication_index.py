#!/usr/bin/env python3
"""Rebuild publication index files from publications/**/*.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PUBLICATIONS = ROOT / "publications"
CATEGORIES = ("journal", "conference")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def publication_sort_key(path: Path) -> tuple[int, str]:
    try:
        data = read_json(path)
        order = int(data.get("order") or 999999)
    except Exception:
        order = 999999
    return order, path.name


def validate_publication(path: Path, year: int, category: str) -> None:
    data = read_json(path)
    if data.get("year") != year:
        raise ValueError(f"{path} has year={data.get('year')}, expected {year}.")
    if data.get("type") != category:
        raise ValueError(f"{path} has type={data.get('type')}, expected {category}.")


def existing_active_map(publications_dir: Path) -> dict[tuple[int, str], bool]:
    manifest_path = publications_dir / "index.json"
    if not manifest_path.exists():
        return {}
    try:
        manifest = read_json(manifest_path)
    except Exception:
        return {}

    active: dict[tuple[int, str], bool] = {}
    for year_data in manifest.get("years", []):
        if not isinstance(year_data, dict):
            continue
        year = year_data.get("year")
        if not isinstance(year, int):
            continue
        for category in CATEGORIES:
            category_data = year_data.get(category)
            if isinstance(category_data, dict):
                active[(year, category)] = bool(category_data.get("active"))
    return active


def discover_years(publications_dir: Path) -> list[int]:
    years = []
    for child in publications_dir.iterdir():
        if child.is_dir() and child.name.isdigit():
            years.append(int(child.name))
    return sorted(years, reverse=True)


def rebuild_indexes(publications_dir: Path, active_year: int | None, dry_run: bool = False) -> dict[str, object]:
    years = discover_years(publications_dir)
    if not years:
        raise FileNotFoundError(f"No publication year directories found in {publications_dir}")

    active_map = existing_active_map(publications_dir)
    if active_year is None and not any(active_map.values()):
        active_year = max(years)

    manifest_years: list[dict[str, object]] = []
    for year in years:
        year_data: dict[str, object] = {"year": year}
        for category in CATEGORIES:
            category_dir = publications_dir / str(year) / category
            if not category_dir.exists():
                continue

            files = sorted(
                [path for path in category_dir.glob("*.json") if path.name != "index.json"],
                key=publication_sort_key,
            )
            for path in files:
                validate_publication(path, year, category)

            if active_year is not None:
                active = year == active_year
            else:
                active = active_map.get((year, category), False)

            category_index = {
                "year": year,
                "type": category,
                "active": active,
                "files": [path.name for path in files],
            }
            if not dry_run:
                write_json(category_dir / "index.json", category_index)

            year_data[category] = {
                "active": active,
                "files": [f"publications/{year}/{category}/{path.name}" for path in files],
            }
        manifest_years.append(year_data)

    manifest = {"years": manifest_years}
    if not dry_run:
        write_json(publications_dir / "index.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="扫描 publications/ 并重建 index.json。")
    parser.add_argument("--publications", type=Path, default=DEFAULT_PUBLICATIONS, help="正式 publications 目录。")
    parser.add_argument("--active-year", type=int, help="默认展开的年份；不传则保留现有设置，若没有现有设置则使用最新年份。")
    parser.add_argument("--dry-run", action="store_true", help="只打印新索引，不写入文件。")
    args = parser.parse_args()

    manifest = rebuild_indexes(args.publications, args.active_year, dry_run=args.dry_run)
    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        total = 0
        for year_data in manifest["years"]:
            for category in CATEGORIES:
                category_data = year_data.get(category)
                if isinstance(category_data, dict):
                    total += len(category_data["files"])
        print(f"已重建 {args.publications / 'index.json'}，共索引 {total} 篇论文。")


if __name__ == "__main__":
    main()
