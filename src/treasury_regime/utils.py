from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from treasury_regime.schemas import to_jsonable


def ensure_parent(path: str | Path) -> Path:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def write_json(path: str | Path, payload: Any) -> Path:
    destination = ensure_parent(path)
    destination.write_text(json.dumps(to_jsonable(payload), indent=2), encoding="utf-8")
    return destination


def read_json(path: str | Path, default: Any = None) -> Any:
    candidate = Path(path)
    if not candidate.exists():
        return default
    return json.loads(candidate.read_text(encoding="utf-8"))


def write_frame(path: str | Path, frame: pd.DataFrame, *, index: bool = True) -> Path:
    destination = ensure_parent(path)
    frame.to_csv(destination, index=index)
    return destination
