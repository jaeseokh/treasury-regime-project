from __future__ import annotations

FRED_SERIES = {
    "DGS3MO": "yield_3m",
    "DGS6MO": "yield_6m",
    "DGS1": "yield_1y",
    "DGS2": "yield_2y",
    "DGS3": "yield_3y",
    "DGS5": "yield_5y",
    "DGS7": "yield_7y",
    "DGS10": "yield_10y",
    "DGS20": "yield_20y",
    "DGS30": "yield_30y",
    "DFII5": "real_5y",
    "DFII10": "real_10y",
    "T5YIE": "breakeven_5y",
    "T10YIE": "breakeven_10y",
    "SOFR": "sofr",
    "DFF": "fed_funds_effective",
    "IORB": "interest_on_reserve_balances",
    "OBFR": "overnight_bank_funding_rate",
    "RRPONTSYD": "reverse_repo_takeup",
    "BAMLH0A0HYM2": "high_yield_spread",
    "DTWEXBGS": "dollar_index",
    "DCOILWTICO": "wti",
    "VIXCLS": "vix",
    "UNRATE": "unemployment_rate",
    "CPIAUCSL": "headline_cpi",
    "CPILFESL": "core_cpi",
    "PCEPILFE": "core_pce",
    "PAYEMS": "nonfarm_payrolls",
    "INDPRO": "industrial_production",
}

TREASURY_SERIES = [
    "yield_3m",
    "yield_6m",
    "yield_1y",
    "yield_2y",
    "yield_3y",
    "yield_5y",
    "yield_7y",
    "yield_10y",
    "yield_20y",
    "yield_30y",
]

PLAYERS = [
    "treasury",
    "federal_reserve",
    "sell_side",
    "buy_side",
    "foreign_official",
]

SOURCE_CHANNELS = [
    "activity_anchor",
    "inflation_regime",
    "policy_framework",
    "treasury_market",
    "shock_player",
]

SHOCK_CATEGORIES = [
    "kinetic_geopolitical",
    "energy_shipping_supply",
    "fiscal_issuance_defense",
    "monetary_credibility",
    "funding_liquidity",
    "narrative_policy_signaling",
]
