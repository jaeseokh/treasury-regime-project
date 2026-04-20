from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from treasury_regime.config import OUTPUT_DIR
from treasury_regime.schemas import ChannelUpdate, PlayerResponse, ShockEvent
from treasury_regime.utils import write_json


@dataclass
class ReportBundle:
    summary: dict[str, object]
    markdown_path: Path
    json_path: Path


class ReportAgent:
    def _decomposition_note(self, row: pd.Series) -> str:
        if row["d_breakeven_10y"] > 0 and row["d_real_10y"] < 0:
            return "Breakevens rose while real yields fell, which is a classic stagflation-style decomposition: inflation fear up, growth confidence down."
        if row["d_breakeven_10y"] > 0 and row["d_real_10y"] > 0:
            return "Breakevens and real yields rose together, which is more consistent with a higher nominal discount-rate regime than a pure stagflation shock."
        if row["d_breakeven_10y"] < 0 and row["d_real_10y"] < 0:
            return "Breakevens and real yields fell together, which is more consistent with growth and policy easing pressure."
        return "Inflation compensation softened while real yields rose, which suggests cleaner disinflation or a term-premium rather than stagflation impulse."

    def _strategy_implications(self, row: pd.Series, dominant_mid_regime: str) -> dict[str, str]:
        direction = "two-way"
        if row["d_yield_10y"] > 0.02:
            direction = "higher_yields"
        elif row["d_yield_10y"] < -0.02:
            direction = "lower_yields"

        if row["curve_2s10s_change"] > 0.015:
            curve = "steepening"
        elif row["curve_2s10s_change"] < -0.015:
            curve = "flattening"
        else:
            curve = "range_bound"

        risk = "fiscal_premium"
        if dominant_mid_regime == "growth_slowdown_constrained_easing":
            risk = "growth_break_lower"
        elif dominant_mid_regime == "war_augmented_inflation_pressure":
            risk = "energy_and_inflation_reacceleration"
        elif dominant_mid_regime == "funding_liquidity_stress":
            risk = "market_functioning"

        return {
            "directional_view": direction,
            "curve_view": curve,
            "main_risk": risk,
            "policy_paralysis_signal": "high" if row["policy_uncertainty_score"] > 1.0 else "medium" if row["policy_uncertainty_score"] > 0.3 else "low",
            "term_premium_view": "rising" if row["d_term_premium_proxy_10y"] > 0 else "falling" if row["d_term_premium_proxy_10y"] < 0 else "stable",
            "falsifier": "A clean reversal in breakevens, repo stress, and long-end underperformance would challenge the current path.",
        }

    def run(
        self,
        market_data: pd.DataFrame,
        features: pd.DataFrame,
        shock_event: ShockEvent,
        regime_summary: dict[str, object],
        channel_updates: list[ChannelUpdate],
        player_responses: list[PlayerResponse],
        source_scorecard: pd.DataFrame,
    ) -> ReportBundle:
        latest_date = market_data.index[-1]
        row = features.loc[latest_date]
        previous = market_data.iloc[-2]
        current = market_data.iloc[-1]
        dominant_mid_regime = regime_summary["dominant_regimes"]["mid"]["regime_id"]
        strategy = self._strategy_implications(row, dominant_mid_regime)

        summary = {
            "date": str(latest_date.date()),
            "war_anchor_date": "2025-06-21",
            "current_regime": regime_summary["dominant_regimes"],
            "shock_event": shock_event,
            "strategy": strategy,
            "curve_snapshot": {
                "yield_2y": float(current["yield_2y"]),
                "yield_10y": float(current["yield_10y"]),
                "curve_2s10s": float(current["curve_2s10s"]),
                "curve_5s30s": float(current["curve_5s30s"]),
                "fly_2s5s10s": float(row["fly_2s5s10s"] * 100.0),
                "fly_5s10s30s": float(row["fly_5s10s30s"] * 100.0),
                "breakeven_10y": float(current["breakeven_10y"]),
                "real_10y": float(current["real_10y"]),
                "expected_short_rate_proxy_2y": float(row["expected_short_rate_proxy_2y"]),
                "term_premium_proxy_10y": float(row["term_premium_proxy_10y"]),
                "term_premium_proxy_30y": float(row["term_premium_proxy_30y"]),
                "expected_short_rate_proxy_10y": float(row["expected_short_rate_proxy_10y"]),
                "ns_level": float(row["ns_level"]),
                "ns_slope": float(row["ns_slope"]),
                "ns_curvature": float(row["ns_curvature"]),
            },
            "daily_changes": {
                "yield_2y_bp": float((current["yield_2y"] - previous["yield_2y"]) * 100.0),
                "yield_10y_bp": float((current["yield_10y"] - previous["yield_10y"]) * 100.0),
                "curve_2s10s_bp": float((current["curve_2s10s"] - previous["curve_2s10s"]) * 100.0),
                "breakeven_10y_bp": float((current["breakeven_10y"] - previous["breakeven_10y"]) * 100.0),
                "real_10y_bp": float((current["real_10y"] - previous["real_10y"]) * 100.0),
                "term_premium_proxy_10y_bp": float((row["term_premium_proxy_10y"] - features.iloc[-2]["term_premium_proxy_10y"]) * 100.0),
                "wti_pct": float((current["wti"] / previous["wti"] - 1.0) * 100.0) if previous["wti"] else 0.0,
            },
            "curve_decomposition": {
                "interpretation": self._decomposition_note(row),
                "policy_uncertainty_score": float(row["policy_uncertainty_score"]),
                "stagflation_signal": float(row["stagflation_signal"]),
                "term_premium_model_window_months": float(row["term_premium_model_window_months"]),
            },
            "risk_measures": {
                "par_price_2y": float(row["par_price_2y"]),
                "par_price_10y": float(row["par_price_10y"]),
                "mod_duration_2y": float(row["mod_duration_2y"]),
                "mod_duration_10y": float(row["mod_duration_10y"]),
                "convexity_2y": float(row["convexity_2y"]),
                "convexity_10y": float(row["convexity_10y"]),
                "price_change_10bp_2y_pct": float(row["price_change_10bp_2y"]),
                "price_change_10bp_10y_pct": float(row["price_change_10bp_10y"]),
                "dv01_2y": float(row["dv01_2y"]),
                "dv01_10y": float(row["dv01_10y"]),
                "dv01_proxy_2y": float(row["dv01_proxy_2y"]),
                "dv01_proxy_10y": float(row["dv01_proxy_10y"]),
            },
            "channel_updates": channel_updates,
            "player_responses": player_responses,
            "source_scorecard": source_scorecard.to_dict(orient="records"),
        }

        markdown_lines = [
            "# Treasury Regime Lab",
            "",
            f"## Date",
            summary["date"],
            "",
            "## Current Regime",
            *(f"- {horizon.title()}: `{payload['regime_id']}` (p={payload['probability']:.2f})" for horizon, payload in summary["current_regime"].items()),
            "",
            "## Shock",
            f"- Dominant shock: `{shock_event.dominant_category}`",
            f"- Transmission: `{shock_event.transmission_channel}`",
            f"- Persistence: `{shock_event.persistence_score:.2f}`",
            f"- Confidence: `{shock_event.confidence_score:.2f}`",
            "",
            "## Treasury Market Snapshot",
            f"- 2Y: `{summary['curve_snapshot']['yield_2y']:.2f}`",
            f"- 10Y: `{summary['curve_snapshot']['yield_10y']:.2f}`",
            f"- 2s10s: `{summary['curve_snapshot']['curve_2s10s'] * 100:.1f}` bp",
            f"- 5s30s: `{summary['curve_snapshot']['curve_5s30s'] * 100:.1f}` bp",
            f"- 2s5s10s fly: `{summary['curve_snapshot']['fly_2s5s10s']:.1f}` bp",
            f"- 5s10s30s fly: `{summary['curve_snapshot']['fly_5s10s30s']:.1f}` bp",
            f"- Nelson-Siegel level/slope/curvature: `{summary['curve_snapshot']['ns_level']:.2f}` / `{summary['curve_snapshot']['ns_slope']:.2f}` / `{summary['curve_snapshot']['ns_curvature']:.2f}`",
            f"- 10Y VAR-style expected short-rate proxy: `{summary['curve_snapshot']['expected_short_rate_proxy_10y']:.2f}`",
            f"- 10Y VAR-style term-premium proxy: `{summary['curve_snapshot']['term_premium_proxy_10y']:.2f}`",
            "",
            "## Curve Decomposition",
            f"- {summary['curve_decomposition']['interpretation']}",
            f"- Policy uncertainty score: `{summary['curve_decomposition']['policy_uncertainty_score']:.2f}`",
            f"- Term-premium model window: `{summary['curve_decomposition']['term_premium_model_window_months']:.0f}` monthly observations",
            "",
            "## Strategy",
            f"- Direction: `{strategy['directional_view']}`",
            f"- Curve: `{strategy['curve_view']}`",
            f"- Term-premium view: `{strategy['term_premium_view']}`",
            f"- Policy paralysis signal: `{strategy['policy_paralysis_signal']}`",
            f"- Main risk: `{strategy['main_risk']}`",
            f"- Falsifier: {strategy['falsifier']}",
            "",
            "## Duration And Convexity",
            f"- Cash-flow basis: semiannual par-bond approximation, price per 100 par `{summary['risk_measures']['par_price_2y']:.2f}` / `{summary['risk_measures']['par_price_10y']:.2f}` for 2Y / 10Y",
            f"- 2Y modified duration / convexity: `{summary['risk_measures']['mod_duration_2y']:.2f}` / `{summary['risk_measures']['convexity_2y']:.2f}`",
            f"- 10Y modified duration / convexity: `{summary['risk_measures']['mod_duration_10y']:.2f}` / `{summary['risk_measures']['convexity_10y']:.2f}`",
            f"- DV01 per 100 par, 2Y / 10Y: `{summary['risk_measures']['dv01_2y']:.4f}` / `{summary['risk_measures']['dv01_10y']:.4f}`",
            f"- Approx. 10 bp price move, 2Y / 10Y: `{summary['risk_measures']['price_change_10bp_2y_pct']:.2f}%` / `{summary['risk_measures']['price_change_10bp_10y_pct']:.2f}%`",
            "",
            "## Player Paths",
        ]
        for response in player_responses:
            markdown_lines.append(f"### {response.player_id.replace('_', ' ').title()}")
            for horizon, scenarios in response.horizon_scenarios.items():
                markdown_lines.append(f"- {horizon.title()}: " + ", ".join(f"`{scenario.action}` ({scenario.probability:.2f})" for scenario in scenarios[:3]))
        markdown_path = OUTPUT_DIR / "daily_report.md"
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text("\n".join(markdown_lines), encoding="utf-8")
        json_path = write_json(OUTPUT_DIR / "daily_summary.json", summary)
        return ReportBundle(summary=summary, markdown_path=markdown_path, json_path=json_path)
