import csv
import re
from collections.abc import Iterable
from io import TextIOWrapper
from pathlib import Path
from typing import Any
from zipfile import ZipFile


def to_positive_float(value: Any) -> float | None:
    if isinstance(value, str):
        value = re.sub(r"[^\d./]", "", value) if value else ""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def term_data(
    csv_path: Path | Iterable[Path], field: str, type_=None
) -> dict[str, Any]:
    paths = csv_path if isinstance(csv_path, Iterable) else [csv_path]
    type_ = type_ if type_ else str
    data = {}
    for path in paths:
        terms = read_terms(path)
        for term in terms:
            value = term.get(field)
            if value not in (None, ""):
                data[term["pattern"]] = type_(value)
    return data


def read_terms(csv_path: Path | Iterable[Path]) -> list[dict]:
    paths = csv_path if isinstance(csv_path, Iterable) else [csv_path]
    terms = []
    for path in paths:
        if path.suffix == ".zip":
            with ZipFile(path) as zippy, zippy.open(f"{path.stem}.csv") as in_csv:
                reader = csv.DictReader(TextIOWrapper(in_csv, "utf-8"))
                terms += list(reader)
        else:
            with open(path) as term_file:
                reader = csv.DictReader(term_file)
                terms += list(reader)
    return terms
