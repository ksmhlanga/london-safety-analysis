import math
import numpy as np
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 100)

CENTROIDS = {
    "Barking and Dagenham": (51.5362, 0.0798), "Barnet": (51.6252, -0.1517),
    "Bexley": (51.4416, 0.1503), "Brent": (51.5673, -0.2713),
    "Bromley": (51.4039, 0.0198), "Camden": (51.5517, -0.1588),
    "City of London": (51.5155, -0.0922), "Croydon": (51.3714, -0.0977),
    "Ealing": (51.5130, -0.3089), "Enfield": (51.6538, -0.0799),
    "Greenwich": (51.4892, 0.0648), "Hackney": (51.5450, -0.0553),
    "Hammersmith and Fulham": (51.4927, -0.2339), "Haringey": (51.5906, -0.1111),
    "Harrow": (51.5836, -0.3464), "Havering": (51.5779, 0.2120),
    "Hillingdon": (51.5441, -0.4760), "Hounslow": (51.4746, -0.3680),
    "Islington": (51.5465, -0.1058), "Kensington and Chelsea": (51.4991, -0.1938),
    "Kingston upon Thames": (51.4085, -0.3064), "Lambeth": (51.4571, -0.1231),
    "Lewisham": (51.4452, -0.0209), "Merton": (51.4014, -0.1988),
    "Newham": (51.5077, 0.0469), "Redbridge": (51.5590, 0.0741),
    "Richmond upon Thames": (51.4479, -0.3260), "Southwark": (51.5035, -0.0804),
    "Sutton": (51.3618, -0.1945), "Tower Hamlets": (51.5099, -0.0059),
    "Waltham Forest": (51.5908, -0.0134), "Wandsworth": (51.4567, -0.1920),
    "Westminster": (51.4975, -0.1357),
}

# Area in km2, ONS/Wikipedia "List of London boroughs"
AREA_KM2 = {
    "Barking and Dagenham": 36.1, "Barnet": 86.7, "Bexley": 60.6, "Brent": 43.3,
    "Bromley": 150.1, "Camden": 21.8, "City of London": 2.9, "Croydon": 86.5,
    "Ealing": 55.5, "Enfield": 82.2, "Greenwich": 47.3, "Hackney": 19.1,
    "Hammersmith and Fulham": 16.4, "Haringey": 29.6, "Harrow": 50.5,
    "Havering": 112.3, "Hillingdon": 115.7, "Hounslow": 56.0, "Islington": 14.9,
    "Kensington and Chelsea": 12.1, "Kingston upon Thames": 37.2, "Lambeth": 26.8,
    "Lewisham": 35.1, "Merton": 37.6, "Newham": 36.2, "Redbridge": 56.4,
    "Richmond upon Thames": 57.4, "Southwark": 28.9, "Sutton": 43.8,
    "Tower Hamlets": 19.8, "Waltham Forest": 38.8, "Wandsworth": 34.3,
    "Westminster": 21.5,
}

INNER = {"Camden","City of London","Greenwich","Hackney","Hammersmith and Fulham",
         "Islington","Kensington and Chelsea","Lambeth","Lewisham","Southwark",
         "Tower Hamlets","Wandsworth","Westminster"}

MILE_KM = 1.609344
CIRCLE_KM2 = math.pi * MILE_KM ** 2

summary = pd.read_csv("data/raw/crime_data_summary.csv")
pop = pd.read_csv("data/raw/borough_population.csv").set_index("borough")["population"]

print(f"Circle area for a 1-mile-radius API query: {CIRCLE_KM2:.2f} km2")
print(f"Total records in summary file: {summary['count'].sum():,}")
print(f"Months: {summary['month'].nunique()}  Boroughs: {summary['borough'].nunique()}")
print(f"Implied crimes per year: {summary['count'].sum()/2:,.0f}")
print("MPS recorded offences 2024/25 (published): ~951,800\n")

tot = summary.groupby("borough")["count"].sum()

df = pd.DataFrame({
    "captured_crimes_24mo": tot,
    "population": pop,
    "area_km2": pd.Series(AREA_KM2),
})
df["inner"] = df.index.isin(INNER)
df["sampled_km2"] = np.minimum(CIRCLE_KM2, df["area_km2"])
df["coverage_pct"] = 100 * df["sampled_km2"] / df["area_km2"]
df["rate_per10k_yr"] = df["captured_crimes_24mo"] / df["population"] * 10000 / 2
# what the rate would look like if the sampled circle were representative of the borough
df["rate_if_scaled"] = df["rate_per10k_yr"] / (df["sampled_km2"] / df["area_km2"])

print("=== Area coverage of the 1-mile sampling circle ===")
print(df.sort_values("coverage_pct")[
    ["area_km2","coverage_pct","captured_crimes_24mo","rate_per10k_yr","rate_if_scaled","inner"]
].round(1).to_string())

print("\n=== Inner vs Outer (as published) ===")
g = df.groupby("inner")
print("mean rate_per10k_yr :", g["rate_per10k_yr"].mean().round(1).to_dict())
print("mean coverage_pct   :", g["coverage_pct"].mean().round(1).to_dict())
print("mean area_km2       :", g["area_km2"].mean().round(1).to_dict())

r = np.corrcoef(df["coverage_pct"], df["rate_per10k_yr"])[0, 1]
print(f"\nPearson r(area coverage %, published crime rate) = {r:.3f}")
r2 = np.corrcoef(np.log(df["area_km2"]), df["rate_per10k_yr"])[0, 1]
print(f"Pearson r(log borough area, published crime rate) = {r2:.3f}")

# ---- overlap between sampling circles ----
def haversine_km(a, b):
    lat1, lon1 = map(math.radians, a); lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))

names = list(CENTROIDS)
pairs = []
for i in range(len(names)):
    for j in range(i+1, len(names)):
        d = haversine_km(CENTROIDS[names[i]], CENTROIDS[names[j]])
        if d < 2 * MILE_KM:
            pairs.append((names[i], names[j], round(d, 2)))
print(f"\n=== Overlapping sampling circles (centroids < 2 miles apart) ===")
print(f"{len(pairs)} overlapping borough pairs out of {len(names)*(len(names)-1)//2}")
for p in sorted(pairs, key=lambda x: x[2]):
    print(f"  {p[0]:<26} {p[1]:<26} {p[2]:>5} km apart")
