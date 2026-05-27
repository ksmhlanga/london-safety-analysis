"""
police_api.py
-------------
Utility functions for interacting with the data.police.uk public API.

No API key required. Documentation: https://data.police.uk/docs/
"""

import time
import requests
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

# Use a try/except so this module can be imported even if config isn't on path
try:
    from src.config import POLICE_API_BASE, BOROUGH_CENTROIDS
except ImportError:
    from config import POLICE_API_BASE, BOROUGH_CENTROIDS


# ── Date helpers ──────────────────────────────────────────────────────────────

def generate_months(start: str, end: str) -> list[str]:
    """
    Return a list of 'YYYY-MM' strings between start and end (inclusive).

    Parameters
    ----------
    start : str  e.g. '2024-01'
    end   : str  e.g. '2024-12'
    """
    current = datetime.strptime(start, "%Y-%m")
    stop    = datetime.strptime(end,   "%Y-%m")
    months  = []
    while current <= stop:
        months.append(current.strftime("%Y-%m"))
        current += relativedelta(months=1)
    return months


# ── API availability ──────────────────────────────────────────────────────────

def get_available_dates() -> list[str]:
    """Return list of months available from data.police.uk (most-recent first)."""
    url = f"{POLICE_API_BASE}/crimes-street-dates"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    dates = [item["date"] for item in resp.json()]
    return sorted(dates, reverse=True)


def latest_available_month() -> str:
    """Return the most-recent month available in the API."""
    return get_available_dates()[0]


# ── Crime fetching ────────────────────────────────────────────────────────────

def fetch_crimes_for_location(
    lat: float,
    lon: float,
    date: str,
    borough_name: str = "",
    retries: int = 3,
    backoff: float = 2.0,
) -> list[dict]:
    """
    Fetch all crimes near a lat/lon centroid for a given month.

    Parameters
    ----------
    lat, lon    : float  Borough centroid
    date        : str    'YYYY-MM'
    borough_name: str    Used to tag each record
    retries     : int    How many times to retry on failure
    backoff     : float  Seconds to wait between retries
    """
    url = f"{POLICE_API_BASE}/crimes-street/all-crime"
    params = {"lat": lat, "lng": lon, "date": date}

    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 503:
                time.sleep(backoff * (attempt + 1))
                continue
            resp.raise_for_status()
            records = resp.json()

            # Tag each record with our borough name and the date
            for rec in records:
                rec["borough"] = borough_name
                rec["query_date"] = date
            return records

        except (requests.exceptions.RequestException, ValueError):
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                return []   # Return empty on final failure
    return []


def fetch_all_boroughs(
    months: list[str],
    centroids: dict | None = None,
    sleep_between: float = 0.3,
) -> pd.DataFrame:
    """
    Fetch crime data for all London boroughs across a list of months.

    Parameters
    ----------
    months         : list[str]  e.g. ['2024-01', '2024-02', ...]
    centroids      : dict       borough -> (lat, lon); defaults to BOROUGH_CENTROIDS
    sleep_between  : float      seconds to sleep between API calls (be polite!)

    Returns
    -------
    pd.DataFrame with one row per crime record
    """
    if centroids is None:
        centroids = BOROUGH_CENTROIDS

    all_records = []
    total = len(centroids) * len(months)

    with tqdm(total=total, desc="Fetching crime data", unit="requests") as pbar:
        for borough, (lat, lon) in centroids.items():
            for month in months:
                records = fetch_crimes_for_location(lat, lon, month, borough)
                all_records.extend(records)
                time.sleep(sleep_between)
                pbar.update(1)
                pbar.set_postfix({"borough": borough[:20], "month": month})

    return _flatten_records(all_records)


# ── Data flattening ───────────────────────────────────────────────────────────

def _flatten_records(records: list[dict]) -> pd.DataFrame:
    """
    Convert raw API records (nested JSON) into a flat DataFrame.

    Relevant fields from data.police.uk:
        category, location_type, location.latitude, location.longitude,
        location.street.id, location.street.name,
        context, outcome_status.category, outcome_status.date,
        persistent_id, id, month, borough, query_date
    """
    rows = []
    for rec in records:
        loc = rec.get("location") or {}
        street = loc.get("street") or {}
        outcome = rec.get("outcome_status") or {}

        rows.append({
            "crime_id":        rec.get("id", ""),
            "persistent_id":   rec.get("persistent_id", ""),
            "month":           rec.get("month", ""),
            "query_date":      rec.get("query_date", ""),
            "borough":         rec.get("borough", ""),
            "crime_type":      rec.get("category", ""),
            "location_type":   rec.get("location_type", ""),
            "latitude":        float(loc.get("latitude") or 0),
            "longitude":       float(loc.get("longitude") or 0),
            "street_id":       street.get("id", ""),
            "street_name":     street.get("name", ""),
            "outcome_category": outcome.get("category", ""),
            "outcome_date":     outcome.get("date", ""),
            "context":         rec.get("context", ""),
        })

    df = pd.DataFrame(rows)

    # Type conversions
    if not df.empty:
        df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
        df["latitude"]  = pd.to_numeric(df["latitude"],  errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    return df
