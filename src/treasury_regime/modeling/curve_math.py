from __future__ import annotations

import numpy as np
import pandas as pd


MATURITY_YEARS = np.array([0.25, 0.50, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0], dtype=float)
CURVE_COLUMNS = [
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


def _yield_to_decimal(yield_value: float) -> float:
    return yield_value / 100.0 if abs(yield_value) > 1.0 else yield_value


def nelson_siegel_loadings(maturity_years: np.ndarray, lambda_value: float) -> np.ndarray:
    scaled = lambda_value * maturity_years
    slope_loading = np.divide(
        1.0 - np.exp(-scaled),
        scaled,
        out=np.ones_like(maturity_years, dtype=float),
        where=scaled != 0,
    )
    curvature_loading = slope_loading - np.exp(-scaled)
    return np.column_stack(
        [
            np.ones_like(maturity_years, dtype=float),
            slope_loading,
            curvature_loading,
        ]
    )


def calibrate_nelson_siegel_lambda(curve_frame: pd.DataFrame) -> float:
    clean = curve_frame.loc[:, CURVE_COLUMNS].dropna(how="any")
    if clean.empty:
        return 0.60

    yields = clean.to_numpy(dtype=float)
    candidates = np.linspace(0.10, 1.50, 57)
    best_lambda = 0.60
    best_sse = np.inf
    for candidate in candidates:
        design = nelson_siegel_loadings(MATURITY_YEARS, float(candidate))
        beta_hat, *_ = np.linalg.lstsq(design, yields.T, rcond=None)
        fitted = design @ beta_hat
        residual = yields.T - fitted
        sse = float(np.square(residual).sum())
        if sse < best_sse:
            best_lambda = float(candidate)
            best_sse = sse
    return best_lambda


def fit_nelson_siegel_factors(curve_frame: pd.DataFrame, lambda_value: float) -> pd.DataFrame:
    design = nelson_siegel_loadings(MATURITY_YEARS, lambda_value)
    records: list[dict[str, float | pd.Timestamp]] = []
    for date, row in curve_frame.loc[:, CURVE_COLUMNS].dropna(how="any").iterrows():
        beta_hat, *_ = np.linalg.lstsq(design, row.to_numpy(dtype=float), rcond=None)
        fitted = design @ beta_hat
        records.append(
            {
                "date": date,
                "ns_lambda": float(lambda_value),
                "ns_level": float(beta_hat[0]),
                "ns_slope": float(beta_hat[1]),
                "ns_curvature": float(beta_hat[2]),
                "ns_fit_10y": float(fitted[7]),
                "ns_resid_5y": float(row["yield_5y"] - fitted[5]),
                "ns_resid_10y": float(row["yield_10y"] - fitted[7]),
            }
        )
    if not records:
        return pd.DataFrame(index=curve_frame.index)
    factors = pd.DataFrame(records).set_index("date").sort_index()
    factors.index = pd.DatetimeIndex(factors.index, name="date")
    return factors


def _par_bond_price(
    coupon_rate: float,
    yield_to_maturity: float,
    maturity_years: float,
    *,
    frequency: int = 2,
    face_value: float = 100.0,
) -> float:
    periods = max(1, int(round(maturity_years * frequency)))
    period_index = np.arange(1, periods + 1, dtype=float)
    coupon_cashflow = face_value * coupon_rate / frequency
    cashflows = np.full(periods, coupon_cashflow, dtype=float)
    cashflows[-1] += face_value
    discount = np.power(1.0 + yield_to_maturity / frequency, period_index)
    return float(np.sum(cashflows / discount))


def estimate_cashflow_bond_risk(
    yield_value: float,
    maturity_years: float,
    *,
    frequency: int = 2,
    face_value: float = 100.0,
    price_shock_bp: float = 10.0,
) -> dict[str, float]:
    yield_decimal = _yield_to_decimal(float(yield_value))
    coupon_rate = max(yield_decimal, 0.0)

    price = _par_bond_price(coupon_rate, yield_decimal, maturity_years, frequency=frequency, face_value=face_value)
    shock_1bp = 1.0 / 10000.0
    price_up_1bp = _par_bond_price(
        coupon_rate,
        yield_decimal + shock_1bp,
        maturity_years,
        frequency=frequency,
        face_value=face_value,
    )
    price_down_1bp = _par_bond_price(
        coupon_rate,
        yield_decimal - shock_1bp,
        maturity_years,
        frequency=frequency,
        face_value=face_value,
    )
    modified_duration = (price_down_1bp - price_up_1bp) / (2.0 * price * shock_1bp)
    convexity = (price_up_1bp + price_down_1bp - 2.0 * price) / (price * shock_1bp * shock_1bp)
    dv01 = (price_down_1bp - price_up_1bp) / 2.0

    shock = price_shock_bp / 10000.0
    price_up = _par_bond_price(
        coupon_rate,
        yield_decimal + shock,
        maturity_years,
        frequency=frequency,
        face_value=face_value,
    )
    price_change_pct = (price_up / price - 1.0) * 100.0
    return {
        "price": price,
        "modified_duration": float(modified_duration),
        "convexity": float(convexity),
        "dv01": float(dv01),
        "price_change_pct": float(price_change_pct),
    }


def estimate_bond_risk_frame(curve_frame: pd.DataFrame, shock_bp: float = 10.0) -> pd.DataFrame:
    records: list[dict[str, float | pd.Timestamp]] = []
    for date, row in curve_frame.loc[:, ["yield_2y", "yield_10y", "yield_30y"]].dropna(how="any").iterrows():
        row_record: dict[str, float | pd.Timestamp] = {"date": date}
        for label, maturity in (("2y", 2.0), ("10y", 10.0), ("30y", 30.0)):
            risk = estimate_cashflow_bond_risk(float(row[f"yield_{label}"]), maturity, price_shock_bp=shock_bp)
            row_record[f"par_price_{label}"] = risk["price"]
            row_record[f"mod_duration_{label}"] = risk["modified_duration"]
            row_record[f"convexity_{label}"] = risk["convexity"]
            row_record[f"price_change_{int(shock_bp)}bp_{label}"] = risk["price_change_pct"]
            row_record[f"dv01_{label}"] = risk["dv01"]
            row_record[f"dv01_proxy_{label}"] = risk["dv01"]
        records.append(row_record)
    if not records:
        return pd.DataFrame(index=curve_frame.index)
    risk = pd.DataFrame(records).set_index("date").sort_index()
    risk.index = pd.DatetimeIndex(risk.index, name="date")
    return risk


def _build_var_state_frame(curve_frame: pd.DataFrame) -> pd.DataFrame:
    state = pd.DataFrame(index=curve_frame.index)
    state["short_rate"] = curve_frame["fed_funds_effective"]
    state["bill_gap"] = curve_frame["yield_3m"] - curve_frame["fed_funds_effective"]
    state["policy_gap_2y"] = curve_frame["yield_2y"] - curve_frame["fed_funds_effective"]
    state["slope_2s10s"] = curve_frame["yield_10y"] - curve_frame["yield_2y"]
    if "ns_curvature" in curve_frame.columns:
        state["curvature"] = curve_frame["ns_curvature"]
    else:
        state["curvature"] = 2.0 * curve_frame["yield_5y"] - curve_frame["yield_2y"] - curve_frame["yield_10y"]
    if "core_pce" in curve_frame.columns:
        state["inflation_gap"] = curve_frame["core_pce"] - 2.0
    elif "core_cpi" in curve_frame.columns:
        state["inflation_gap"] = curve_frame["core_cpi"] - 2.0
    else:
        state["inflation_gap"] = np.nan
    state["unemployment_gap"] = curve_frame["unemployment_rate"] - 4.2
    state = state.sort_index().ffill().dropna(how="any")
    monthly = state.resample("ME").last().dropna(how="any")
    monthly.index = pd.DatetimeIndex(monthly.index, name="date")
    return monthly


def _fit_centered_var1(state_window: pd.DataFrame, ridge_alpha: float = 0.10) -> tuple[np.ndarray, np.ndarray]:
    sample = state_window.to_numpy(dtype=float)
    mean = sample.mean(axis=0)
    x_prev = sample[:-1] - mean
    x_next = sample[1:] - mean
    if x_prev.shape[0] < 2:
        return mean, np.zeros((sample.shape[1], sample.shape[1]), dtype=float)

    xtx = x_prev.T @ x_prev + ridge_alpha * np.eye(x_prev.shape[1], dtype=float)
    coef = np.linalg.solve(xtx, x_prev.T @ x_next)
    spectral_radius = float(np.max(np.abs(np.linalg.eigvals(coef)))) if coef.size else 0.0
    if spectral_radius > 0.985:
        coef *= 0.985 / spectral_radius
    return mean, coef


def _forecast_average_short_rate(
    last_observation: np.ndarray,
    mean: np.ndarray,
    coef: np.ndarray,
    horizon_months: int,
    *,
    short_rate_floor: float = -1.0,
    short_rate_cap: float = 12.0,
) -> float:
    state = last_observation - mean
    short_rates: list[float] = []
    for _ in range(max(1, horizon_months)):
        state = state @ coef
        projected = state + mean
        short_rates.append(float(np.clip(projected[0], short_rate_floor, short_rate_cap)))
    return float(np.mean(short_rates))


def build_term_premium_proxy(curve_frame: pd.DataFrame) -> pd.DataFrame:
    monthly_state = _build_var_state_frame(curve_frame)
    if monthly_state.empty:
        return pd.DataFrame(index=curve_frame.index)

    rolling_window_months = 120
    min_observations = 36
    records: list[dict[str, float | pd.Timestamp]] = []
    for index in range(min_observations - 1, len(monthly_state.index)):
        window = monthly_state.iloc[max(0, index - rolling_window_months + 1) : index + 1]
        mean, coef = _fit_centered_var1(window)
        last_observation = window.iloc[-1].to_numpy(dtype=float)
        expected_short_2y = _forecast_average_short_rate(last_observation, mean, coef, 24)
        expected_short_10y = _forecast_average_short_rate(last_observation, mean, coef, 120)
        expected_short_30y = _forecast_average_short_rate(last_observation, mean, coef, 360)
        records.append(
            {
                "date": monthly_state.index[index],
                "expected_short_rate_proxy_2y": expected_short_2y,
                "expected_short_rate_proxy_10y": expected_short_10y,
                "expected_short_rate_proxy_30y": expected_short_30y,
                "term_premium_model_window_months": float(len(window.index)),
            }
        )

    if not records:
        return pd.DataFrame(index=curve_frame.index)

    monthly_proxy = pd.DataFrame(records).set_index("date").sort_index()
    daily = monthly_proxy.reindex(curve_frame.index).ffill()
    daily["term_premium_proxy_2y"] = curve_frame["yield_2y"] - daily["expected_short_rate_proxy_2y"]
    daily["term_premium_proxy_10y"] = curve_frame["yield_10y"] - daily["expected_short_rate_proxy_10y"]
    daily["term_premium_proxy_30y"] = curve_frame["yield_30y"] - daily["expected_short_rate_proxy_30y"]
    return daily.loc[
        :,
        [
            "expected_short_rate_proxy_2y",
            "expected_short_rate_proxy_10y",
            "expected_short_rate_proxy_30y",
            "term_premium_proxy_2y",
            "term_premium_proxy_10y",
            "term_premium_proxy_30y",
            "term_premium_model_window_months",
        ],
    ]
