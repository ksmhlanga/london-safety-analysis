# London Safety Analysis

![London](assets/london-banner.jpg)

### Data-driven borough safety analysis for family relocation decisions

![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Records](https://img.shields.io/badge/Records-753%2C904-orange)
![Boroughs](https://img.shields.io/badge/Boroughs-33-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ksmhlanga-london-safety-analysis.streamlit.app)

---

## 🌐 Live App

**[👉 Open the Interactive Dashboard](https://ksmhlanga-london-safety-analysis.streamlit.app)**

Explore borough safety rankings, crime trends, the family finder tool, and the embedded Power BI dashboard — all live online.

---

## Personal Story

In 2025, I faced a real decision: relocating my family from Northern Ireland to London for better career opportunities. As a father, safety and school quality mattered most. As a PSV Mechanic transitioning into Data Analytics, I chose to treat it as a data project rather than rely on guesswork or estate agent recommendations.

London has 33 boroughs. Each varies widely in crime levels, school quality, housing cost, and liveability. This project documents how I used publicly available data to identify the safest, most family-friendly boroughs — and built a complete end-to-end analytics pipeline along the way.

---

## Project Summary

| Metric | Value |
|---|---|
| Crime records analysed | 753,904 |
| Boroughs covered | 33 |
| Date range | January 2024 – December 2025 |
| Data source | data.police.uk (public API, no key required) |
| Safest borough | Barnet (100 / 100) |
| Best for families | Bromley, Bexley, Havering, Redbridge, Kingston |
| Highest risk | City of London, Westminster, Kensington and Chelsea |

---

## Key Findings

**Safest boroughs overall**

| Rank | Borough | Safety Score | Tier |
|---|---|---|---|
| 1 | Barnet | 100 / 100 | Excellent |
| 2 | Bromley | 99.6 / 100 | Excellent |
| 3 | Redbridge | 99.4 / 100 | Excellent |
| 4 | Bexley | 99.4 / 100 | Excellent |
| 5 | Havering | 99.4 / 100 | Excellent |

**Top 5 boroughs for families** (safety + affordability + outer London location)

| Rank | Borough | Family Score | Avg House Price | Zone |
|---|---|---|---|---|
| 1 | Bromley | 89.8 | £500,000 | Outer |
| 2 | Bexley | 89.7 | £360,000 | Outer |
| 3 | Redbridge | 89.7 | £420,000 | Outer |
| 4 | Havering | 89.7 | £355,000 | Outer |
| 5 | Kingston upon Thames | 89.6 | £500,000 | Outer |

**Statistical insights**

- Borough crime differences are highly significant (one-way ANOVA, p < 0.001) — choosing the right borough genuinely matters
- Outer London boroughs are 40–60% safer on average than central areas
- Violence and robbery are strongly correlated across boroughs (r > 0.85)
- Crime follows seasonal patterns: violent crime peaks in summer, burglary peaks in winter
- K-means clustering identifies 4 distinct borough crime profiles

---

## Methodology

### Safety Score (0–100)

Each borough is scored using a weighted composite of crime rates per 10,000 residents. Higher score = safer.

| Crime type | Weight | Rationale |
|---|---|---|
| Violence & sexual offences | 30% | Highest personal threat |
| Robbery | 20% | Direct confrontation |
| Burglary | 15% | Home invasion |
| Criminal damage / arson | 10% | Property and physical risk |
| Drugs | 8% | Environmental safety signal |
| Vehicle crime | 7% | Practical daily impact |
| Theft from person | 5% | Minor personal impact |
| Anti-social behaviour | 3% | Liveability signal |

### Family Score (0–100)

A secondary composite score designed specifically for families:
- Safety score — 50%
- Housing affordability (vs London median) — 30%
- Outer London location — 20%

### Analysis Pipeline

| Step | Notebook | Description |
|---|---|---|
| 1 | `01_data_collection` | Fetch crime data from data.police.uk API |
| 2 | `02_data_exploration` | Exploratory data analysis (EDA) |
| 3 | `03_data_cleaning` | Handle missing values, standardise formats |
| 4 | `04_feature_engineering` | Build composite Safety Score |
| 5 | `05_statistical_analysis` | ANOVA, K-means clustering, trend detection |
| 6 | `06_visualisations` | Interactive dashboard, Folium map, recommendations |

---

## 🚀 Streamlit Web App

**Live URL:** [https://ksmhlanga-london-safety-analysis.streamlit.app](https://ksmhlanga-london-safety-analysis.streamlit.app)

The project includes a fully interactive web app built with Streamlit, bringing all the analysis to life in a browser without needing to run any code.

### App Pages

| Page | Description |
|---|---|
| 🏠 Overview | KPI cards (total crimes, avg safety score, avg house price, crime rate) + full borough safety rankings bar chart |
| 🗺️ Borough Map | Interactive scatter map of London coloured by safety score, family score, or house price |
| ⚖️ Compare Boroughs | Select up to 3 boroughs and compare side by side — radar chart, crime breakdown, monthly trend |
| 👨‍👩‍👧 Family Finder | Sliders for budget, safety priority and transport preference — returns a ranked list of best boroughs for your family |
| 📊 Power BI Dashboard | Embedded live Power BI report with crime trends, family suitability, and borough breakdowns |

### Running Locally

```bash
pip install streamlit pandas plotly numpy
streamlit run app.py
```

---

## Repository Structure

```
london-safety-analysis/
├── data/
│   ├── raw/                          # Original data from API
│   │   ├── crime_data_raw.csv        # 611,509 crime records
│   │   ├── borough_population.csv    # 2021 census populations
│   │   └── crime_data_summary.csv    # Monthly borough totals
│   ├── processed/
│   │   ├── crime_data_clean.csv      # Cleaned analysis-ready data
│   │   └── borough_safety_summary.csv # Final scores per borough
│   └── external/                     # Reference data (GeoJSON etc.)
├── notebooks/
│   ├── 00_project_overview.ipynb
│   ├── 01_data_collection.ipynb
│   ├── 02_data_exploration.ipynb
│   ├── 03_data_cleaning.ipynb
│   ├── 04_feature_engineering.ipynb
│   ├── 05_statistical_analysis.ipynb
│   └── 06_visualisations.ipynb
├── reports/
│   └── figures/                      # Saved charts (PNG)
├── dashboards/
│   ├── london_safety_dashboard.html  # Interactive Plotly dashboard
│   └── london_safety_map.html        # Interactive Folium map
├── src/
│   ├── config.py                     # Constants, centroids, weights
│   ├── police_api.py                 # API helper functions
│   ├── scoring.py                    # Safety score algorithm
│   └── collect_data.py               # Standalone data collection script
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Technologies Used

| Category | Tools |
|---|---|
| Language | Python 3.8+ |
| Data manipulation | Pandas, NumPy |
| Statistical analysis | SciPy, Statsmodels |
| Machine learning | Scikit-learn (K-Means, PCA, MinMaxScaler) |
| Visualisation | Matplotlib, Seaborn, Plotly, Folium |
| API integration | Requests (data.police.uk) |
| Environment | Jupyter Notebooks |
| Version control | Git, GitHub |

---

## Skills Demonstrated

- End-to-end data analytics pipeline
- Public API integration (data.police.uk)
- Data cleaning and preprocessing at scale (611k records)
- Feature engineering and composite scoring systems
- Statistical hypothesis testing (ANOVA)
- Unsupervised machine learning (K-Means clustering, PCA)
- Interactive data visualisation (Plotly, Folium)
- Reproducible research with Jupyter notebooks
- Git version control and GitHub portfolio management

---

## Project Checklist

- [x] Define research question and project scope
- [x] Set up repository structure
- [x] Collect crime data via data.police.uk API (611,509 records)
- [x] Collect borough population data (ONS 2021 census)
- [x] Exploratory data analysis (EDA)
- [x] Data cleaning and standardisation
- [x] Feature engineering — composite Safety Score (0–100)
- [x] Feature engineering — Family Suitability Score
- [x] Statistical hypothesis testing (one-way ANOVA)
- [x] K-means clustering of boroughs by crime profile
- [x] Time-series trend analysis per borough
- [x] Interactive Plotly dashboard
- [x] Interactive Folium borough safety map
- [x] Borough safety ranking chart (publication quality)
- [x] Final recommendations for families

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/ksmhlanga/london-safety-analysis.git
cd london-safety-analysis

# Install dependencies
pip install -r requirements.txt

# (Optional) Refresh data from the live API
python src/collect_data.py

# Open the notebooks
jupyter notebook notebooks/
```

Run the notebooks in order from `01` through to `06`. The data files are already included so you can run the analysis immediately without calling the API.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Author

**Kudzanayi Shepherd Mhlanga**

PSV Mechanic transitioning into Data Analytics | Newcastle, Northern Ireland

- Email: ksmhlanga@gmail.com
- LinkedIn: [linkedin.com/in/ksmhlanga](https://www.linkedin.com/in/ksmhlanga)
- GitHub: [github.com/ksmhlanga](https://github.com/ksmhlanga)
- Portfolio: [datascienceportfol.io/ksmhlanga](https://www.datascienceportfol.io/ksmhlanga)

---

*"Data-driven decisions for life's important moments."*
