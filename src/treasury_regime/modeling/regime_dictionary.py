from __future__ import annotations

from treasury_regime.schemas import RegimeDefinition


REGIME_DEFINITIONS = [
    RegimeDefinition(
        regime_id="policy_trapped_stagflation_risk",
        regime_name="Policy-Trapped Stagflation Risk",
        regime_family="late_cycle",
        economic_definition="Inflation remains sticky enough to constrain easing while growth and labor momentum soften.",
        inflation_state="sticky_above_target",
        growth_state="decelerating",
        labor_state="softening_orderly",
        policy_state="restrictive_but_constrained",
        financial_state="fragile_not_broken",
        fiscal_geopolitical_state="elevated_uncertainty",
        treasury_signature=[
            "front-end remains elevated",
            "curve inversion only partially heals",
            "breakevens stay firm",
            "long-end embeds term premium uncertainty",
        ],
        entry_conditions=[
            "core inflation stops converging cleanly to target",
            "labor cools without collapse",
            "policy guidance avoids a fast cutting cycle",
        ],
        exit_conditions=[
            "inflation re-anchors cleanly",
            "growth slips into deeper slowdown",
            "war or fiscal premium forces a new inflation leg",
        ],
        allowed_next_regimes=[
            "war_augmented_inflation_pressure",
            "growth_slowdown_constrained_easing",
            "fiscal_term_premium_repricing",
        ],
    ),
    RegimeDefinition(
        regime_id="war_augmented_inflation_pressure",
        regime_name="War-Augmented Inflation Pressure",
        regime_family="shock_overlay",
        economic_definition="Geopolitical escalation raises energy, shipping, and risk premia while constraining policy flexibility.",
        inflation_state="reacceleration_risk",
        growth_state="fragile_resilience",
        labor_state="secondary_importance",
        policy_state="look_through_or_tight_bias",
        financial_state="risk_off_with_inflation",
        fiscal_geopolitical_state="high_geopolitical_stress",
        treasury_signature=[
            "breakevens and oil move together",
            "front-end reprices policy path uncertainty",
            "long-end oscillates between haven demand and fiscal premium",
        ],
        entry_conditions=[
            "kinetic or energy shock raises inflation persistence concerns",
            "official sources warn on uncertainty and supply channels",
        ],
        exit_conditions=[
            "shock fades quickly",
            "energy impulse reverses",
            "market transitions into fiscal premium or growth slowdown regime",
        ],
        allowed_next_regimes=[
            "fiscal_term_premium_repricing",
            "growth_slowdown_constrained_easing",
            "reanchoring_normalization",
        ],
    ),
    RegimeDefinition(
        regime_id="growth_slowdown_constrained_easing",
        regime_name="Growth Slowdown With Constrained Easing",
        regime_family="slowdown",
        economic_definition="Growth deteriorates, but the Fed remains unable to ease aggressively because inflation credibility is still unfinished.",
        inflation_state="still_above_target_but_falling",
        growth_state="below_trend",
        labor_state="softening_clearer",
        policy_state="reluctant_easing_bias",
        financial_state="moderate_stress",
        fiscal_geopolitical_state="contained",
        treasury_signature=[
            "bull steepening pressure grows",
            "credit widens",
            "front-end falls faster than long-end unless fiscal premium intervenes",
        ],
        entry_conditions=[
            "credit and labor soften materially",
            "inflation is no longer the only problem",
        ],
        exit_conditions=[
            "Fed eases and economy stabilizes",
            "slowdown becomes outright funding stress",
        ],
        allowed_next_regimes=[
            "funding_liquidity_stress",
            "reanchoring_normalization",
        ],
    ),
    RegimeDefinition(
        regime_id="fiscal_term_premium_repricing",
        regime_name="Fiscal Term Premium Repricing",
        regime_family="long_end",
        economic_definition="Treasury supply, funding credibility, and global demand concerns push the term premium structurally higher.",
        inflation_state="secondary_but_not_ignored",
        growth_state="mixed",
        labor_state="secondary",
        policy_state="policy_not_main_driver",
        financial_state="long_end_strain",
        fiscal_geopolitical_state="high_deficit_high_supply",
        treasury_signature=[
            "10s30s cheapen versus front-end",
            "auction reception and dealer take-up matter more",
            "safe-haven status becomes conditional",
        ],
        entry_conditions=[
            "heavy issuance or defense financing intensifies",
            "long-end underperforms despite slower growth",
        ],
        exit_conditions=[
            "foreign and private demand re-anchors",
            "Fed or Treasury stabilizes supply expectations",
        ],
        allowed_next_regimes=[
            "funding_liquidity_stress",
            "reanchoring_normalization",
            "war_augmented_inflation_pressure",
        ],
    ),
    RegimeDefinition(
        regime_id="funding_liquidity_stress",
        regime_name="Funding and Liquidity Stress",
        regime_family="market_functioning",
        economic_definition="Funding pressure, dealer balance-sheet strain, or disorderly market functioning dominates macro interpretation.",
        inflation_state="deprioritized_short_run",
        growth_state="stress_sensitive",
        labor_state="lagging_indicator",
        policy_state="stability_tools_relevant",
        financial_state="acute_stress",
        fiscal_geopolitical_state="background_or_trigger",
        treasury_signature=[
            "funding spreads widen",
            "repo proxies become stressed",
            "curve moves become flow-distorted and volatile",
        ],
        entry_conditions=[
            "SOFR and repo proxies gap wider",
            "vol spikes alongside market-functioning concerns",
        ],
        exit_conditions=[
            "funding stress normalizes",
            "policy backstop restores function",
        ],
        allowed_next_regimes=[
            "growth_slowdown_constrained_easing",
            "reanchoring_normalization",
        ],
    ),
    RegimeDefinition(
        regime_id="reanchoring_normalization",
        regime_name="Re-Anchoring Normalization",
        regime_family="normalization",
        economic_definition="Inflation expectations re-anchor, policy credibility improves, and Treasury pricing returns to a cleaner macro transmission.",
        inflation_state="converging_to_target",
        growth_state="stable_or_soft_landing",
        labor_state="balanced",
        policy_state="measured_normalization",
        financial_state="stable",
        fiscal_geopolitical_state="contained",
        treasury_signature=[
            "curve transmission is cleaner",
            "rate volatility trends lower",
            "term premium is less disorderly",
        ],
        entry_conditions=[
            "inflation and policy uncertainty both decline",
            "shock persistence falls",
        ],
        exit_conditions=[
            "new inflation or fiscal shock emerges",
            "growth deteriorates materially",
        ],
        allowed_next_regimes=[
            "policy_trapped_stagflation_risk",
            "growth_slowdown_constrained_easing",
        ],
    ),
]

REGIME_INDEX = {definition.regime_id: definition for definition in REGIME_DEFINITIONS}

INITIAL_REGIME_PRIOR = {
    "policy_trapped_stagflation_risk": 0.36,
    "war_augmented_inflation_pressure": 0.18,
    "growth_slowdown_constrained_easing": 0.16,
    "fiscal_term_premium_repricing": 0.16,
    "funding_liquidity_stress": 0.06,
    "reanchoring_normalization": 0.08,
}

BASE_TRANSITION_MATRIX = {
    "policy_trapped_stagflation_risk": {
        "policy_trapped_stagflation_risk": 0.58,
        "war_augmented_inflation_pressure": 0.16,
        "growth_slowdown_constrained_easing": 0.14,
        "fiscal_term_premium_repricing": 0.08,
        "funding_liquidity_stress": 0.01,
        "reanchoring_normalization": 0.03,
    },
    "war_augmented_inflation_pressure": {
        "policy_trapped_stagflation_risk": 0.18,
        "war_augmented_inflation_pressure": 0.52,
        "growth_slowdown_constrained_easing": 0.09,
        "fiscal_term_premium_repricing": 0.16,
        "funding_liquidity_stress": 0.02,
        "reanchoring_normalization": 0.03,
    },
    "growth_slowdown_constrained_easing": {
        "policy_trapped_stagflation_risk": 0.08,
        "war_augmented_inflation_pressure": 0.04,
        "growth_slowdown_constrained_easing": 0.58,
        "fiscal_term_premium_repricing": 0.05,
        "funding_liquidity_stress": 0.15,
        "reanchoring_normalization": 0.10,
    },
    "fiscal_term_premium_repricing": {
        "policy_trapped_stagflation_risk": 0.14,
        "war_augmented_inflation_pressure": 0.14,
        "growth_slowdown_constrained_easing": 0.08,
        "fiscal_term_premium_repricing": 0.52,
        "funding_liquidity_stress": 0.08,
        "reanchoring_normalization": 0.04,
    },
    "funding_liquidity_stress": {
        "policy_trapped_stagflation_risk": 0.06,
        "war_augmented_inflation_pressure": 0.03,
        "growth_slowdown_constrained_easing": 0.25,
        "fiscal_term_premium_repricing": 0.06,
        "funding_liquidity_stress": 0.46,
        "reanchoring_normalization": 0.14,
    },
    "reanchoring_normalization": {
        "policy_trapped_stagflation_risk": 0.18,
        "war_augmented_inflation_pressure": 0.04,
        "growth_slowdown_constrained_easing": 0.10,
        "fiscal_term_premium_repricing": 0.04,
        "funding_liquidity_stress": 0.02,
        "reanchoring_normalization": 0.62,
    },
}


def regime_ids() -> list[str]:
    return [definition.regime_id for definition in REGIME_DEFINITIONS]
