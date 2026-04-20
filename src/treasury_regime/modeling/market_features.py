from __future__ import annotations

import numpy as np
import pandas as pd

from treasury_regime.modeling.curve_math import (
    build_term_premium_proxy,
    calibrate_nelson_siegel_lambda,
    estimate_bond_risk_frame,
    fit_nelson_siegel_factors,
)


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _first_present(frame: pd.DataFrame, candidates: list[str]) -> pd.Series:
    for column in candidates:
        if column in frame.columns:
            return _safe_numeric(frame[column])
    return pd.Series(np.nan, index=frame.index)


def summarize_auctions(auction_history: pd.DataFrame, upcoming_auctions: pd.DataFrame) -> pd.DataFrame:
    if auction_history.empty:
        return pd.DataFrame()

    frame = auction_history.copy()
    date_column = "auction_date" if "auction_date" in frame.columns else "record_date"
    frame[date_column] = pd.to_datetime(frame[date_column], errors="coerce")
    frame = frame.dropna(subset=[date_column]).sort_values(date_column)
    frame["date"] = frame[date_column]
    frame["bid_to_cover_ratio"] = _first_present(frame, ["bid_to_cover_ratio", "bid_cover_ratio"])
    frame["tail_basis_points"] = _first_present(frame, ["tail_basis_points", "tail"])
    frame["dealer_award_share"] = _first_present(
        frame,
        ["primary_dealer_accepted", "primary_dealer_awarded", "direct_bidder_accepted"],
    )

    daily = frame.groupby("date", as_index=True).agg(
        auction_count=("date", "size"),
        avg_bid_to_cover=("bid_to_cover_ratio", "mean"),
        avg_tail_bp=("tail_basis_points", "mean"),
        avg_dealer_award=("dealer_award_share", "mean"),
    )
    daily.index = pd.DatetimeIndex(daily.index, name="date")
    daily = daily.sort_index()
    daily["auction_count_20d"] = daily["auction_count"].rolling(20, min_periods=1).sum()
    daily["avg_bid_to_cover_20d"] = daily["avg_bid_to_cover"].rolling(20, min_periods=1).mean()
    daily["avg_tail_bp_20d"] = daily["avg_tail_bp"].rolling(20, min_periods=1).mean()
    daily["avg_dealer_award_20d"] = daily["avg_dealer_award"].rolling(20, min_periods=1).mean()

    upcoming_count = len(upcoming_auctions.index) if not upcoming_auctions.empty else 0
    daily["upcoming_auction_count"] = float(upcoming_count)
    return daily


def zscore(series: pd.Series, window: int = 60) -> pd.Series:
    rolling_mean = series.rolling(window, min_periods=max(10, window // 4)).mean()
    rolling_std = series.rolling(window, min_periods=max(10, window // 4)).std(ddof=0)
    return ((series - rolling_mean) / rolling_std.replace(0.0, np.nan)).fillna(0.0)


def build_market_features(market_data: pd.DataFrame, auction_summary: pd.DataFrame | None = None) -> pd.DataFrame:
    features = market_data.copy().sort_index()
    features.index = pd.DatetimeIndex(features.index, name="date")

    ns_lambda = calibrate_nelson_siegel_lambda(features)
    ns_factors = fit_nelson_siegel_factors(features, ns_lambda)
    features = features.join(ns_factors, how="left")
    term_premium_proxy = build_term_premium_proxy(features)
    bond_risk = estimate_bond_risk_frame(features)
    features = features.join(term_premium_proxy, how="left").join(bond_risk, how="left")

    for column in [
        "yield_2y",
        "yield_5y",
        "yield_10y",
        "yield_30y",
        "real_10y",
        "breakeven_10y",
        "sofr",
        "overnight_bank_funding_rate",
        "high_yield_spread",
        "dollar_index",
        "wti",
        "vix",
        "term_premium_proxy_10y",
        "term_premium_proxy_30y",
        "ns_level",
        "ns_slope",
        "ns_curvature",
    ]:
        if column in features.columns:
            features[f"d_{column}"] = features[column].diff()

    features["curve_2s10s_change"] = features["curve_2s10s"].diff()
    features["curve_5s30s_change"] = features["curve_5s30s"].diff()
    features["fly_2s5s10s"] = 2.0 * features["yield_5y"] - features["yield_2y"] - features["yield_10y"]
    features["fly_5s10s30s"] = 2.0 * features["yield_10y"] - features["yield_5y"] - features["yield_30y"]
    features["front_end_vol_20d"] = features["d_yield_2y"].rolling(20, min_periods=10).std(ddof=0)
    features["long_end_vol_20d"] = features["d_yield_10y"].rolling(20, min_periods=10).std(ddof=0)
    features["curve_vol_20d"] = features["curve_2s10s_change"].rolling(20, min_periods=10).std(ddof=0)

    features["z_2y_move"] = zscore(features["d_yield_2y"])
    features["z_10y_move"] = zscore(features["d_yield_10y"])
    features["z_curve_2s10s"] = zscore(features["curve_2s10s"])
    features["z_curve_5s30s"] = zscore(features["curve_5s30s"])
    features["z_fly_2s5s10s"] = zscore(features["fly_2s5s10s"])
    features["z_fly_5s10s30s"] = zscore(features["fly_5s10s30s"])
    features["z_breakeven"] = zscore(features["breakeven_10y"])
    features["z_real_10y"] = zscore(features["real_10y"])
    features["z_repo_minus_sofr"] = zscore(features["repo_minus_sofr"])
    features["z_sofr_minus_ff"] = zscore(features["sofr_minus_ff"])
    features["z_hy_spread"] = zscore(features["high_yield_spread"])
    features["z_dollar"] = zscore(features["dollar_index"])
    features["z_wti"] = zscore(features["wti"])
    features["z_vix"] = zscore(features["vix"])
    features["z_reverse_repo"] = zscore(features["reverse_repo_takeup"])
    features["z_ns_level"] = zscore(features["ns_level"])
    features["z_ns_slope"] = zscore(features["ns_slope"])
    features["z_ns_curvature"] = zscore(features["ns_curvature"])
    features["z_term_premium_2y"] = zscore(features["term_premium_proxy_2y"])
    features["z_term_premium_10y"] = zscore(features["term_premium_proxy_10y"])
    features["z_term_premium_30y"] = zscore(features["term_premium_proxy_30y"])

    features["inflation_pressure_score"] = (
        0.35 * features["z_breakeven"]
        + 0.25 * features["z_wti"]
        + 0.20 * features["z_2y_move"]
        + 0.20 * features["z_real_10y"]
    )
    features["growth_slowdown_score"] = (
        0.35 * features["z_hy_spread"]
        + 0.25 * features["z_vix"]
        - 0.20 * features["z_10y_move"]
        - 0.20 * features["z_wti"]
    )
    features["policy_constraint_score"] = (
        0.45 * features["z_2y_move"]
        - 0.25 * features["z_curve_2s10s"]
        + 0.15 * features["z_real_10y"]
        + 0.15 * features["z_breakeven"]
    )
    features["funding_stress_score"] = (
        0.35 * features["z_repo_minus_sofr"]
        + 0.30 * features["z_sofr_minus_ff"]
        + 0.20 * features["z_vix"]
        + 0.15 * features["z_hy_spread"]
    )
    features["fiscal_term_premium_score"] = (
        0.25 * features["z_curve_5s30s"]
        + 0.25 * features["z_10y_move"]
        + 0.25 * features["z_term_premium_10y"]
        - 0.20 * features["z_2y_move"]
        - 0.15 * features["z_dollar"]
    )
    features["term_premium_slope_score"] = features["z_term_premium_30y"] - features["z_term_premium_2y"]
    features["policy_uncertainty_score"] = (
        0.40 * features["z_ns_curvature"]
        + 0.30 * features["z_fly_2s5s10s"].abs()
        + 0.30 * features["z_fly_5s10s30s"].abs()
    )
    features["stagflation_signal"] = (
        (features["d_breakeven_10y"] > 0).astype(float)
        * (features["d_real_10y"] < 0).astype(float)
    )

    if auction_summary is not None and not auction_summary.empty:
        features = features.join(auction_summary, how="left")
        for column in [
            "auction_count_20d",
            "avg_bid_to_cover_20d",
            "avg_tail_bp_20d",
            "avg_dealer_award_20d",
            "upcoming_auction_count",
        ]:
            if column in features.columns:
                features[column] = features[column].ffill().fillna(0.0)
        if "avg_tail_bp_20d" in features.columns:
            features["z_auction_tail"] = zscore(features["avg_tail_bp_20d"])
            features["fiscal_term_premium_score"] = features["fiscal_term_premium_score"] + 0.12 * features["z_auction_tail"]
        if "avg_bid_to_cover_20d" in features.columns:
            features["z_bid_to_cover"] = zscore(features["avg_bid_to_cover_20d"])
            features["fiscal_term_premium_score"] = features["fiscal_term_premium_score"] - 0.08 * features["z_bid_to_cover"]

    features["transition_pressure"] = (
        0.30 * features["inflation_pressure_score"].abs()
        + 0.25 * features["growth_slowdown_score"].abs()
        + 0.20 * features["funding_stress_score"].abs()
        + 0.15 * features["fiscal_term_premium_score"].abs()
        + 0.10 * features["policy_uncertainty_score"].abs()
    )
    return features.dropna(how="all")
