"""
scoring.py
----------
Functions for computing the composite Safety Score (0–100) per borough.

Higher score = safer borough.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

try:
    from src.config import CRIME_WEIGHTS, LONDON_BOROUGHS
except ImportError:
    from config import CRIME_WEIGHTS, LONDON_BOROUGHS


# ── Borough-level crime rate table ────────────────────────────────────────────

def compute_crime_rates(df: pd.DataFrame, population: dict | None = None) -> pd.DataFrame:
    """
    Compute crime counts (and optionally rates per 10,000 residents) per borough.

    Parameters
    ----------
    df         : raw crime DataFrame
    population : dict  {borough: population}; if None, uses raw counts

    Returns
    -------
    DataFrame indexed by borough with columns for each crime_type count
    """
    pivot = (
        df.groupby(["borough", "crime_type"])
        .size()
        .reset_index(name="count")
        .pivot(index="borough", columns="crime_type", values="count")
        .fillna(0)
    )

    if population:
        for borough in pivot.index:
            pop = population.get(borough, 1)
            pivot.loc[borough] = pivot.loc[borough] / pop * 10_000

    return pivot


# ── Safety score calculation ──────────────────────────────────────────────────

def compute_safety_score(
    crime_rates: pd.DataFrame,
    weights: dict | None = None,
) -> pd.Series:
    """
    Compute a weighted safety score (0–100) for each borough.

    Algorithm
    ---------
    1. For each crime type that has a non-zero weight, normalise counts to 0–1
       (0 = most crime, 1 = least crime).
    2. Multiply by weight and sum → raw_danger_score (higher = more dangerous).
    3. Invert and scale to 0–100 → safety_score (100 = safest).

    Parameters
    ----------
    crime_rates : DataFrame  (boroughs × crime_type columns)
    weights     : dict       {crime_type: weight}; defaults to CRIME_WEIGHTS

    Returns
    -------
    pd.Series  indexed by borough, values 0–100
    """
    if weights is None:
        weights = CRIME_WEIGHTS

    scaler = MinMaxScaler()
    danger_components = []

    for crime_type, weight in weights.items():
        if weight == 0:
            continue
        if crime_type not in crime_rates.columns:
            continue

        col = crime_rates[crime_type].values.reshape(-1, 1)
        # Scale so that 0 = fewest crimes (safest), 1 = most crimes (most dangerous)
        scaled = scaler.fit_transform(col).flatten()
        danger_components.append(scaled * weight)

    if not danger_components:
        return pd.Series(50.0, index=crime_rates.index, name="safety_score")

    # Sum weighted danger components
    danger_score = np.sum(danger_components, axis=0)

    # Invert: safety = 1 - danger, then scale to 0–100
    max_d = danger_score.max()
    if max_d > 0:
        danger_norm = danger_score / max_d
    else:
        danger_norm = danger_score

    safety = (1 - danger_norm) * 100

    return pd.Series(safety, index=crime_rates.index, name="safety_score").round(1)


# ── Borough summary table ─────────────────────────────────────────────────────

def build_borough_summary(
    df: pd.DataFrame,
    population: dict | None = None,
    weights: dict | None = None,
) -> pd.DataFrame:
    """
    Build a full summary table: crime counts, rates, and safety scores.

    Returns
    -------
    DataFrame with columns:
        borough, total_crimes, violent_crimes, property_crimes,
        drug_crimes, asb_incidents, safety_score, safety_tier
    """
    if df.empty:
        return pd.DataFrame()

    # Totals per borough
    totals = df.groupby("borough").size().rename("total_crimes")

    # Key category aggregations
    violent = (
        df[df["crime_type"].isin(["violence-and-sexual-offences", "robbery"])]
        .groupby("borough")
        .size()
        .rename("violent_crimes")
    )

    property_c = (
        df[df["crime_type"].isin(["burglary", "theft-from-the-person",
                                   "vehicle-crime", "shoplifting", "bicycle-theft"])]
        .groupby("borough")
        .size()
        .rename("property_crimes")
    )

    drugs = (
        df[df["crime_type"] == "drugs"]
        .groupby("borough")
        .size()
        .rename("drug_crimes")
    )

    asb = (
        df[df["crime_type"] == "anti-social-behaviour"]
        .groupby("borough")
        .size()
        .rename("asb_incidents")
    )

    # Safety score
    crime_rates = compute_crime_rates(df, population)
    safety = compute_safety_score(crime_rates, weights)

    summary = (
        pd.concat([totals, violent, property_c, drugs, asb, safety], axis=1)
        .fillna(0)
        .reset_index()
        .rename(columns={"index": "borough"})
    )

    # Add safety tier label
    summary["safety_tier"] = pd.cut(
        summary["safety_score"],
        bins=[0, 40, 60, 75, 90, 100],
        labels=["High Risk", "Elevated", "Moderate", "Good", "Excellent"],
        include_lowest=True,
    )

    # Rank
    summary = summary.sort_values("safety_score", ascending=False).reset_index(drop=True)
    summary.insert(0, "rank", range(1, len(summary) + 1))

    return summary


# ── Tier colour palette for charts ───────────────────────────────────────────
TIER_COLOURS = {
    "Excellent": "#2ecc71",   # green
    "Good":      "#27ae60",   # dark green
    "Moderate":  "#f39c12",   # amber
    "Elevated":  "#e67e22",   # orange
    "High Risk": "#e74c3c",   # red
}
