"""JSONL loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jsonl_with_lines(path: str | Path) -> list[tuple[int, dict[str, Any]]]:
    """Records paired with the 1-based file line each came from.

    Blank lines are skipped, so a record's index is not its line number. Keep
    the pairing when a caller needs to point a reader back at the file.
    """
    records: list[tuple[int, dict[str, Any]]] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {error}") from error
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            records.append((line_number, value))
    return records


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return [record for _, record in load_jsonl_with_lines(path)]
