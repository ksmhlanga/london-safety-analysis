"""
Data Collection Module for London Safety Analysis.

Canonical Stage 2 MVP workflow:
- save borough coordinates reference
- collect police.uk street crime data for London borough centre-point locations
- export raw CSV and metadata JSON for downstream preprocessing

Notes
-----
This MVP uses approximate borough centre coordinates as collection points.
That makes the workflow reproducible in Colab/Drive, but it is still an
approximation of borough-level crime conditions.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class CollectionMetadata:
    project_root: str
    raw_dir: str
    start_date_requested: str
    end_date_requested: str
    start_date_collected: str
    end_date_collected: str
    months_requested: List[str]
    months_collected: List[str]
    borough_count: int
    rows_collected: int
    rows_per_borough: Dict[str, int]
    failed_requests: List[Dict[str, str]]
    output_file: str
    coordinates_file: str
    collection_method: str = "police.uk street crime API using borough centre coordinates"
    notes: str = (
        "This is a Stage 2 MVP raw data extract. "
        "Borough centre coordinates are an approximation and will be improved later."
    )


class CrimeDataCollector:
    BASE_URL = "https://data.police.uk/api"

    def __init__(self, rate_limit: float = 0.35, session: Optional[requests.Session] = None):
        self.rate_limit = rate_limit
        self.last_request_time = 0.0
        self.session = session or requests.Session()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=60)
        self.last_request_time = time.time()
        response.raise_for_status()
        return response.json()

    def get_crimes_by_location(self, lat: float, lng: float, date: str) -> pd.DataFrame:
        data = self._make_request(
            "crimes-street/all-crime",
            params={"lat": lat, "lng": lng, "date": date}
        )
        return pd.DataFrame(data)


class BoroughDataLoader:
    BOROUGH_COORDS = {
        "Barking and Dagenham": (51.5607, 0.1557),
        "Barnet": (51.6256, -0.2083),
        "Bexley": (51.4590, 0.1420),
        "Brent": (51.5590, -0.2760),
        "Bromley": (51.3670, 0.0140),
        "Camden": (51.5410, -0.1420),
        "Croydon": (51.3710, -0.1090),
        "Ealing": (51.5130, -0.3020),
        "Enfield": (51.6540, -0.0800),
        "Greenwich": (51.4890, 0.0050),
        "Hackney": (51.5450, -0.0700),
        "Hammersmith and Fulham": (51.4930, -0.2230),
        "Haringey": (51.5880, -0.1020),
        "Harrow": (51.5800, -0.3360),
        "Havering": (51.5590, 0.1860),
        "Hillingdon": (51.5440, -0.4530),
        "Hounslow": (51.4680, -0.3620),
        "Islington": (51.5380, -0.1050),
        "Kensington and Chelsea": (51.5020, -0.1950),
        "Kingston upon Thames": (51.4090, -0.3040),
        "Lambeth": (51.5010, -0.1150),
        "Lewisham": (51.4450, -0.0200),
        "Merton": (51.4090, -0.2000),
        "Newham": (51.5250, 0.0260),
        "Redbridge": (51.5590, 0.0820),
        "Richmond upon Thames": (51.4470, -0.3030),
        "Southwark": (51.5030, -0.0800),
        "Sutton": (51.3620, -0.1960),
        "Tower Hamlets": (51.5100, -0.0200),
        "Waltham Forest": (51.5880, -0.0200),
        "Wandsworth": (51.4570, -0.1940),
        "Westminster": (51.4970, -0.1350),
        "City of London": (51.5150, -0.0920)
    }

    @classmethod
    def get_borough_list(cls) -> List[str]:
        return list(cls.BOROUGH_COORDS.keys())

    @classmethod
    def get_coordinates(cls, borough: str) -> Tuple[float, float]:
        return cls.BOROUGH_COORDS[borough]

    @classmethod
    def to_dataframe(cls) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"borough": borough, "latitude": lat, "longitude": lng}
                for borough, (lat, lng) in cls.BOROUGH_COORDS.items()
            ]
        )


def ensure_project_paths(project_root: str) -> Dict[str, str]:
    raw_dir = os.path.join(project_root, "data", "raw")
    processed_dir = os.path.join(project_root, "data", "processed")
    external_dir = os.path.join(project_root, "data", "external")
    reports_dir = os.path.join(project_root, "reports")

    for path in [raw_dir, processed_dir, external_dir, reports_dir]:
        os.makedirs(path, exist_ok=True)

    return {
        "project_root": project_root,
        "raw_dir": raw_dir,
        "processed_dir": processed_dir,
        "external_dir": external_dir,
        "reports_dir": reports_dir,
    }


def generate_month_strings(start_date: str, end_date: str) -> List[str]:
    months = pd.date_range(start=start_date, end=end_date, freq="MS")
    return [month.strftime("%Y-%m") for month in months]


def save_borough_coordinates(output_file: str) -> pd.DataFrame:
    coords_df = BoroughDataLoader.to_dataframe()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    coords_df.to_csv(output_file, index=False)
    logger.info("Saved borough coordinates to %s", output_file)
    return coords_df


def collect_crime_data_for_all_boroughs(
    start_date: str,
    end_date: str,
    project_root: str,
    output_filename: str = "crime_data_raw.csv",
    metadata_filename: str = "collection_metadata.json",
    coordinates_filename: str = "borough_coordinates.csv",
    rate_limit: float = 0.35,
):
    paths = ensure_project_paths(project_root)
    raw_dir = paths["raw_dir"]

    output_file = os.path.join(raw_dir, output_filename)
    metadata_file = os.path.join(raw_dir, metadata_filename)
    coordinates_file = os.path.join(raw_dir, coordinates_filename)

    save_borough_coordinates(coordinates_file)

    collector = CrimeDataCollector(rate_limit=rate_limit)
    boroughs = BoroughDataLoader.get_borough_list()
    months_requested = generate_month_strings(start_date, end_date)

    frames: List[pd.DataFrame] = []
    failed_requests: List[Dict[str, str]] = []
    rows_per_borough: Dict[str, int] = {borough: 0 for borough in boroughs}

    logger.info(
        "Collecting crime data for %s boroughs across %s month(s)",
        len(boroughs),
        len(months_requested),
    )

    for borough in tqdm(boroughs, desc="Boroughs"):
        lat, lng = BoroughDataLoader.get_coordinates(borough)
        for month in tqdm(months_requested, desc=f"{borough} months", leave=False):
            try:
                crimes = collector.get_crimes_by_location(lat, lng, month)
                if crimes.empty:
                    continue

                crimes["borough"] = borough
                crimes["borough_latitude"] = lat
                crimes["borough_longitude"] = lng
                crimes["collection_month"] = month
                frames.append(crimes)
                rows_per_borough[borough] += len(crimes)
            except Exception as exc:
                logger.warning("Failed request for %s / %s: %s", borough, month, exc)
                failed_requests.append(
                    {"borough": borough, "month": month, "error": str(exc)}
                )

    if frames:
        combined = pd.concat(frames, ignore_index=True)
    else:
        combined = pd.DataFrame()

    if not combined.empty:
        combined.to_csv(output_file, index=False)
        logger.info("Saved %s rows to %s", len(combined), output_file)
        months_collected = sorted(combined["collection_month"].astype(str).unique().tolist())
        start_collected = min(months_collected)
        end_collected = max(months_collected)
    else:
        months_collected = []
        start_collected = ""
        end_collected = ""

    metadata = CollectionMetadata(
        project_root=project_r