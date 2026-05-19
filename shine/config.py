"""Runtime configuration for Shine.

Reads from environment variables (optionally a .env file) and exposes a
single :class:`Settings` instance via :func:`get_settings`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import List

try:  # python-dotenv is optional at import time
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv missing in some envs
    pass


@dataclass(frozen=True)
class Settings:
    odds_api_key: str = ""
    regions: List[str] = field(default_factory=lambda: ["us", "uk", "eu"])
    odds_format: str = "american"
    cache_ttl: int = 120
    cache_dir: Path = Path(".shine_cache")

    @property
    def has_api_key(self) -> bool:
        return bool(self.odds_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    regions_env = os.getenv("SHINE_REGIONS", "us,uk,eu")
    cache_dir = Path(os.getenv("SHINE_CACHE_DIR", ".shine_cache"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return Settings(
        odds_api_key=os.getenv("ODDS_API_KEY", ""),
        regions=[r.strip() for r in regions_env.split(",") if r.strip()],
        odds_format=os.getenv("SHINE_ODDS_FORMAT", "american"),
        cache_ttl=int(os.getenv("SHINE_CACHE_TTL", "120")),
        cache_dir=cache_dir,
    )
