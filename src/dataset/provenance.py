"""Conferência da cópia local usada pelo projeto."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def inspect_snapshot(monsters: pd.DataFrame, manifest: dict, root: Path = PROJECT_ROOT) -> dict:
    """Compara o arquivo bruto, o manifesto e os IDs do conjunto processado em uso."""
    raw_path = root / "data/raw/monsters_raw_srd2014.json"
    try:
        content = raw_path.read_bytes()
        raw = json.loads(content)
        if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
            raise ValueError("O snapshot bruto deve conter uma lista de registros.")
    except (OSError, ValueError):
        return {"available": False, "verified": False, "processed_count": len(monsters)}
    digest = hashlib.sha256(content).hexdigest()
    same_ids = {item.get("index") for item in raw} == set(monsters["index"])
    same_count = len(raw) == len(monsters) == manifest.get("collected_records_count")
    hash_matches = digest == manifest.get("raw_file_sha256")
    return {"available": True, "verified": hash_matches and same_ids and same_count,
            "hash_matches": hash_matches, "same_ids": same_ids, "same_count": same_count,
            "raw_count": len(raw), "processed_count": len(monsters), "sha256": digest}
