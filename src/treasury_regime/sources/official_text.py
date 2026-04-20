from __future__ import annotations

import hashlib
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from treasury_regime.schemas import EvidenceClaim


FED_PRESS_URL = "https://www.federalreserve.gov/newsevents/pressreleases.htm"
FED_SPEECH_URL = "https://www.federalreserve.gov/newsevents/speeches.htm"
TREASURY_REMARKS_URL = "https://home.treasury.gov/news/press-releases/statements-remarks"


def _claim_id(*parts: str) -> str:
    digest = hashlib.sha1("::".join(parts).encode("utf-8")).hexdigest()
    return digest[:16]


def _keyword_axis(text: str) -> tuple[str, str, str]:
    lowered = text.lower()
    if any(word in lowered for word in ("inflation", "price", "pce", "cpi")):
        return "inflation", "up", "inflation_expectations"
    if any(word in lowered for word in ("labor", "employment", "unemployment", "jobs")):
        return "growth", "down", "growth_labor"
    if any(word in lowered for word in ("auction", "refunding", "issuance", "debt")):
        return "fiscal", "up", "issuance_supply"
    if any(word in lowered for word in ("liquidity", "funding", "repo", "market functioning")):
        return "funding", "up", "funding_liquidity"
    return "policy", "flat", "policy_framework"


def _infer_horizon(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ("today", "near term", "next meeting", "immediate", "short run")):
        return "short"
    if any(word in lowered for word in ("coming months", "this year", "next quarter", "over coming months")):
        return "mid"
    return "long"


def _fetch_html(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def fetch_fed_press_claims(limit: int = 8) -> list[EvidenceClaim]:
    soup = _fetch_html(FED_PRESS_URL)
    claims: list[EvidenceClaim] = []
    for item in soup.select(".eventlist li")[:limit]:
        link = item.select_one("a")
        if link is None:
            continue
        title = link.get_text(" ", strip=True)
        date_text = item.select_one(".date")
        published_at = date_text.get_text(" ", strip=True) if date_text else ""
        axis, direction, channel = _keyword_axis(title)
        claims.append(
            EvidenceClaim(
                claim_id=_claim_id("fed_press", title, published_at),
                source_name="Federal Reserve press releases",
                source_family="policy_framework",
                source_type="official_release",
                published_at=published_at,
                title=title,
                summary=title,
                url=urljoin(FED_PRESS_URL, link.get("href", "")),
                linked_player="federal_reserve",
                regime_axis=axis,
                expected_direction=direction,
                expected_channel=channel,
                horizon=_infer_horizon(title),
                confidence=0.78,
            )
        )
    return claims


def fetch_fed_speech_claims(limit: int = 8) -> list[EvidenceClaim]:
    soup = _fetch_html(FED_SPEECH_URL)
    claims: list[EvidenceClaim] = []
    for item in soup.select(".eventlist li")[:limit]:
        link = item.select_one("a")
        if link is None:
            continue
        title = link.get_text(" ", strip=True)
        published_at = item.select_one(".date").get_text(" ", strip=True) if item.select_one(".date") else ""
        axis, direction, channel = _keyword_axis(title)
        claims.append(
            EvidenceClaim(
                claim_id=_claim_id("fed_speech", title, published_at),
                source_name="Federal Reserve speeches",
                source_family="policy_framework",
                source_type="official_speech",
                published_at=published_at,
                title=title,
                summary=title,
                url=urljoin(FED_SPEECH_URL, link.get("href", "")),
                linked_player="federal_reserve",
                regime_axis=axis,
                expected_direction=direction,
                expected_channel=channel,
                horizon=_infer_horizon(title),
                confidence=0.72,
            )
        )
    return claims


def fetch_treasury_claims(limit: int = 8) -> list[EvidenceClaim]:
    soup = _fetch_html(TREASURY_REMARKS_URL)
    claims: list[EvidenceClaim] = []
    for item in soup.select("article, .views-row")[:limit]:
        link = item.select_one("a")
        if link is None:
            continue
        title = link.get_text(" ", strip=True)
        published_at = item.get_text(" ", strip=True)
        axis, direction, channel = _keyword_axis(title)
        claims.append(
            EvidenceClaim(
                claim_id=_claim_id("treasury", title, published_at),
                source_name="U.S. Treasury statements and remarks",
                source_family="policy_framework",
                source_type="official_statement",
                published_at=published_at,
                title=title,
                summary=title,
                url=urljoin(TREASURY_REMARKS_URL, link.get("href", "")),
                linked_player="treasury",
                regime_axis=axis,
                expected_direction=direction,
                expected_channel=channel,
                horizon=_infer_horizon(title),
                confidence=0.7,
            )
        )
    return claims


def fetch_official_claims() -> list[EvidenceClaim]:
    claims: list[EvidenceClaim] = []
    for fetcher in (fetch_fed_press_claims, fetch_fed_speech_claims, fetch_treasury_claims):
        try:
            claims.extend(fetcher())
        except requests.RequestException:
            continue
    return claims
