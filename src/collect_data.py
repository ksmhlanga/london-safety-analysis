"""
collect_data.py
---------------
Standalone script to fetch real crime data from data.police.uk public API.
Run this from your local machine (internet access required).

Usage:
    python src/collect_data.py

Output:
    data/raw/crime_data_raw.csv          -- all crime records
    data/raw/crime_data_summary.csv      -- borough-level monthly totals
    data/raw/fetch_metadata.json         -- run info (dates fetched, counts)
"""

import sys
import json
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

# ── Ensure project root is on path ───────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import (
    BOROUGH_CENTROIDS, DATA_RAW,
    ANALYSIS_START, ANALYSIS_END,
)

# ── Date range ────────────────────────────────────────────────────────────────
def generate_months(start: str, end: str) -> list:
    from dateutil.relativedelta import relativedelta
    current = datetime.strptime(start, "%Y-%m")
    stop    = datetime.strptime(end,   "%Y-%m")
    months  = []
    while current <= stop:
        months.append(current.strftime("%Y-%m"))
        current += relativedelta(months=1)
    return months


# ── Single API call ───────────────────────────────────────────────────────────
def fetch_month(lat, lon, date, borough, retries=3):
    url = "https://data.police.uk/api/crimes-street/all-crime"
    for attempt in range(retries):
        try:
            r = requests.get(url, params={"lat": lat, "lng": lon, "date": date}, timeout=30)
            if r.status_code == 503:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            records = r.json()
            for rec in records:
                rec["borough"]    = borough
                rec["query_date"] = date
            return records
        except Exception as e:
            print(f"  Warning: {borough} {date} attempt {attempt+1}: {e}")
            time.sleep(2 ** attempt)
    return []


# ── Flatten nested JSON ───────────────────────────────────────────────────────
def flatten(records):
    rows = []
    for rec in records:
        loc    = rec.get("location") or {}
        street = loc.get("street") or {}
        out    = rec.get("outcome_status") or {}
        rows.append({
            "crime_id":         rec.get("id", ""),
            "month":            rec.get("month", ""),
            "borough":          rec.get("borough", ""),
            "crime_type":       rec.get("category", ""),
            "latitude":         loc.get("latitude", ""),
            "longitude":        loc.get("longitude", ""),
            "street_name":      street.get("name", ""),
            "outcome_category": out.get("category", ""),
            "outcome_date":     out.get("date", ""),
        })
    return rows


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  London Safety Analysis — Data Collection")
    print(f"  Date range: {ANALYSIS_START} to {ANALYSIS_END}")
    print(f"  Boroughs:   {len(BOROUGH_CENTROIDS)}")
    print("=" * 60)

    # Check what dates are available from the API
    try:
        available = requests.get(
            "https://data.police.uk/api/crimes-street-dates", timeout=20
        ).json()
        api_dates = sorted([d["date"] for d in available])
        print(f"\nAPI data available from {api_dates[0]} to {api_dates[-1]}")
        # Clip our range to what's available
        start = max(ANALYSIS_START, api_dates[0])
        end   = min(ANALYSIS_END,   api_dates[-1])
        print(f"Fetching: {start} to {end}\n")
    except Exception as e:
        print(f"Could not check API dates: {e}")
        start, end = ANALYSIS_START, ANALYSIS_END

    months = generate_months(start, end)
    total  = len(BOROUGH_CENTROIDS) * len(months)
    print(f"Total API calls: {total} ({len(months)} months × {len(BOROUGH_CENTROIDS)} boroughs)")
    print("Estimated time: ~{:.0f} minutes\n".format(total * 0.4 / 60))

    all_records = []
    done = 0
    for borough, (lat, lon) in BOROUGH_CENTROIDS.items():
        for month in months:
            records = fetch_month(lat, lon, month, borough)
            all_records.extend(records)
            done += 1
            if done % 10 == 0:
                pct = done / total * 100
                print(f"  Progress: {done}/{total} ({pct:.0f}%) — {borough[:25]}, {month}")
            time.sleep(0.35)   # Be polite to the API

    print(f"\nTotal records fetched: {len(all_records):,}")

    # Flatten and save
    rows = flatten(all_records)
    df   = pd.DataFrame(rows)
    df   = df.drop_duplicates(subset=["crime_id", "borough", "month"])

    out_raw = DATA_RAW / "crime_data_raw.csv"
    df.to_csv(out_raw, index=False)
    print(f"Saved: {out_raw}  ({len(df):,} rows)")

    # Borough monthly summary
    summary = (
        df.groupby(["borough", "month", "crime_type"])
        .size()
        .reset_index(name="count")
    )
    out_summary = DATA_RAW / "crime_data_summary.csv"
    summary.to_csv(out_summary, index=False)
    print(f"Saved: {out_summary}  ({len(summary):,} rows)")

    # Metadata
    metadata = {
        "fetched_at":    datetime.now().isoformat(),
        "date_range":    {"start": start, "end": end},
        "months_fetched": months,
        "total_records": len(df),
        "boroughs":      list(BOROUGH_CENTROIDS.keys()),
    }
    out_meta = DATA_RAW / "fetch_metadata.json"
    with open(out_meta, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved: {out_meta}")
    print("\nData collection complete.")


if __name__ == "__main__":
    main()
