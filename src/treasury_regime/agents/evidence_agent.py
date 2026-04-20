from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from treasury_regime.config import MANUAL_DIR, PROCESSED_DIR
from treasury_regime.schemas import EvidenceClaim
from treasury_regime.sources.official_text import fetch_official_claims
from treasury_regime.utils import read_json, write_json


@dataclass
class EvidenceBundle:
    claims: list[EvidenceClaim]
    frame: pd.DataFrame
    path: Path


class EvidenceAgent:
    def __init__(self, manual_claims_path: Path | None = None) -> None:
        self.manual_claims_path = manual_claims_path or (MANUAL_DIR / "manual_media_claims.json")

    def _load_manual_claims(self) -> list[EvidenceClaim]:
        payload = read_json(self.manual_claims_path, default=[])
        claims: list[EvidenceClaim] = []
        for item in payload:
            try:
                claims.append(EvidenceClaim(**item))
            except TypeError:
                continue
        return claims

    def run(self) -> EvidenceBundle:
        claims = fetch_official_claims() + self._load_manual_claims()
        frame = pd.DataFrame(
            [
                {
                    "claim_id": claim.claim_id,
                    "source_name": claim.source_name,
                    "source_family": claim.source_family,
                    "source_type": claim.source_type,
                    "published_at": claim.published_at,
                    "title": claim.title,
                    "summary": claim.summary,
                    "url": claim.url,
                    "linked_player": claim.linked_player,
                    "regime_axis": claim.regime_axis,
                    "expected_direction": claim.expected_direction,
                    "expected_channel": claim.expected_channel,
                    "horizon": claim.horizon,
                    "confidence": claim.confidence,
                }
                for claim in claims
            ]
        )
        if not frame.empty:
            frame["published_at"] = pd.to_datetime(frame["published_at"], errors="coerce", format="mixed")
            frame = frame.sort_values("published_at", ascending=False).reset_index(drop=True)
        path = write_json(PROCESSED_DIR / "evidence_claims.json", [claim for claim in claims])
        return EvidenceBundle(claims=claims, frame=frame, path=path)
