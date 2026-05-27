"""
config.py
---------
Central configuration for the London Safety Analysis project.
All paths, API endpoints, and constants live here.
"""

from pathlib import Path

# ── Project root ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent

# ── Data directories ──────────────────────────────────────────────────────────
DATA_RAW       = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_EXTERNAL  = ROOT / "data" / "external"

# ── Report & dashboard directories ───────────────────────────────────────────
REPORTS_DIR    = ROOT / "reports"
FIGURES_DIR    = REPORTS_DIR / "figures"
DASHBOARDS_DIR = ROOT / "dashboards"

# Create dirs if they don't exist
for d in [DATA_RAW, DATA_PROCESSED, DATA_EXTERNAL, FIGURES_DIR, DASHBOARDS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── data.police.uk API ────────────────────────────────────────────────────────
POLICE_API_BASE    = "https://data.police.uk/api"
POLICE_FORCES_URL  = f"{POLICE_API_BASE}/forces"
POLICE_CRIMES_URL  = f"{POLICE_API_BASE}/crimes-street/all-crime"
POLICE_OUTCOMES_URL = f"{POLICE_API_BASE}/outcomes-at-location"

# Metropolitan Police Service covers all 32 London boroughs
LONDON_FORCE = "metropolitan"

# ── London Boroughs ───────────────────────────────────────────────────────────
# 32 boroughs + City of London (for completeness)
LONDON_BOROUGHS = [
    "Barking and Dagenham",
    "Barnet",
    "Bexley",
    "Brent",
    "Bromley",
    "Camden",
    "City of London",
    "Croydon",
    "Ealing",
    "Enfield",
    "Greenwich",
    "Hackney",
    "Hammersmith and Fulham",
    "Haringey",
    "Harrow",
    "Havering",
    "Hillingdon",
    "Hounslow",
    "Islington",
    "Kensington and Chelsea",
    "Kingston upon Thames",
    "Lambeth",
    "Lewisham",
    "Merton",
    "Newham",
    "Redbridge",
    "Richmond upon Thames",
    "Southwark",
    "Sutton",
    "Tower Hamlets",
    "Waltham Forest",
    "Wandsworth",
    "Westminster",
]

# Approximate borough centroids (lat, lon) for API calls
# Source: Google Maps / ONS
BOROUGH_CENTROIDS = {
    "Barking and Dagenham": (51.5362, 0.0798),
    "Barnet":               (51.6252, -0.1517),
    "Bexley":               (51.4416, 0.1503),
    "Brent":                (51.5673, -0.2713),
    "Bromley":              (51.4039, 0.0198),
    "Camden":               (51.5517, -0.1588),
    "City of London":       (51.5155, -0.0922),
    "Croydon":              (51.3714, -0.0977),
    "Ealing":               (51.5130, -0.3089),
    "Enfield":              (51.6538, -0.0799),
    "Greenwich":            (51.4892, 0.0648),
    "Hackney":              (51.5450, -0.0553),
    "Hammersmith and Fulham": (51.4927, -0.2339),
    "Haringey":             (51.5906, -0.1111),
    "Harrow":               (51.5836, -0.3464),
    "Havering":             (51.5779, 0.2120),
    "Hillingdon":           (51.5441, -0.4760),
    "Hounslow":             (51.4746, -0.3680),
    "Islington":            (51.5465, -0.1058),
    "Kensington and Chelsea": (51.4991, -0.1938),
    "Kingston upon Thames": (51.4085, -0.3064),
    "Lambeth":              (51.4571, -0.1231),
    "Lewisham":             (51.4452, -0.0209),
    "Merton":               (51.4014, -0.1988),
    "Newham":               (51.5077, 0.0469),
    "Redbridge":            (51.5590, 0.0741),
    "Richmond upon Thames": (51.4479, -0.3260),
    "Southwark":            (51.5035, -0.0804),
    "Sutton":               (51.3618, -0.1945),
    "Tower Hamlets":        (51.5099, -0.0059),
    "Waltham Forest":       (51.5908, -0.0134),
    "Wandsworth":           (51.4567, -0.1920),
    "Westminster":          (51.4975, -0.1357),
}

# ── Crime type weights for safety score ───────────────────────────────────────
# Higher weight = worse impact on safety score
CRIME_WEIGHTS = {
    "violence-and-sexual-offences":   0.30,
    "robbery":                         0.20,
    "burglary":                        0.15,
    "criminal-damage-arson":          0.10,
    "drugs":                           0.08,
    "vehicle-crime":                   0.07,
    "theft-from-the-person":          0.05,
    "shoplifting":                     0.02,
    "anti-social-behaviour":          0.03,
    "other-crime":                     0.00,   # excluded from score
    "other-theft":                     0.00,
    "possession-of-weapons":          0.00,
    "public-order":                    0.00,
    "bicycle-theft":                   0.00,
    "computer-crime":                  0.00,
    "miscellaneous-incidents":         0.00,
}

# ── Analysis date range ────────────────────────────────────────────────────────
# data.police.uk provides monthly data; we fetch 24 months
ANALYSIS_START = "2024-01"   # YYYY-MM
ANALYSIS_END   = "2025-12"   # YYYY-MM  (adjust as API data allows)
