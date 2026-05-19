"""Shared JSON loading + name normalization."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=16)
def load_json(name: str) -> dict:
    path = DATA_DIR / name
    return json.loads(path.read_text())


_PUNCT = re.compile(r"[^a-z0-9\s]")


def normalize_name(name: str) -> str:
    n = (name or "").lower().strip()
    n = _PUNCT.sub("", n)
    n = re.sub(r"\s+", " ", n)
    return n
