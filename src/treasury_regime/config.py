from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MANUAL_DIR = DATA_DIR / "manual"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

DEFAULT_WEBSITE_ROOT = Path(
    os.getenv("TREASURY_REGIME_WEBSITE_ROOT", "/Users/jaeseokhwang/jaeseok_website")
)
WEBSITE_DATA_DIR = DEFAULT_WEBSITE_ROOT / "assets" / "data"


@dataclass(frozen=True)
class HorizonConfig:
    label: str
    days_min: int
    days_max: int
    treasury_weight: float
    shock_weight: float
    policy_weight: float
    inflation_weight: float
    activity_weight: float


HORIZONS = {
    "short": HorizonConfig(
        label="short",
        days_min=0,
        days_max=10,
        treasury_weight=0.36,
        shock_weight=0.27,
        policy_weight=0.17,
        inflation_weight=0.12,
        activity_weight=0.08,
    ),
    "mid": HorizonConfig(
        label="mid",
        days_min=20,
        days_max=90,
        treasury_weight=0.27,
        shock_weight=0.18,
        policy_weight=0.24,
        inflation_weight=0.21,
        activity_weight=0.10,
    ),
    "long": HorizonConfig(
        label="long",
        days_min=180,
        days_max=730,
        treasury_weight=0.18,
        shock_weight=0.12,
        policy_weight=0.24,
        inflation_weight=0.24,
        activity_weight=0.22,
    ),
}


WAR_ANCHOR_DATE = "2025-06-21"
SECONDARY_ESCALATION_DATE = "2026-02-28"
