"""
London Safety Analysis — Streamlit App
========================================
Interactive web app for exploring borough safety data.
Run locally:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="London Safety Analysis",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).resolve().parent
SUMMARY_FILE = ROOT / "data" / "processed" / "borough_safety_summary.csv"
CRIMES_FILE  = ROOT / "data" / "raw"       / "crime_data_summary.csv"

# ── Transport data (approximate — TfL zones & nearest tube/rail) ──────────────
TRANSPORT = {
    "Barnet":                {"zone": "4-5", "links": "Northern line, Thameslink"},
    "Bromley":               {"zone": "4-6", "links": "Overground, Southeastern"},
    "Redbridge":             {"zone": "3-4", "links": "Central line, Elizabeth line"},
    "Bexley":                {"zone": "4-6", "links": "Southeastern rail"},
    "Havering":              {"zone": "5-6", "links": "Elizabeth line, c2c"},
    "Sutton":                {"zone": "4-5", "links": "Thameslink, Southern"},
    "Hillingdon":            {"zone": "4-6", "links": "Metropolitan, Piccadilly lines"},
    "Wandsworth":            {"zone": "2-3", "links": "Northern line, Overground"},
    "Harrow":                {"zone": "4-5", "links": "Metropolitan, Bakerloo lines"},
    "Ealing":                {"zone": "3-4", "links": "Central, District, Elizabeth lines"},
    "Enfield":               {"zone": "4-6", "links": "Piccadilly line, Overground"},
    "Richmond upon Thames":  {"zone": "4",   "links": "District line, Overground"},
    "Kingston upon Thames":  {"zone": "6",   "links": "Southwestern rail"},
    "Greenwich":             {"zone": "3-4", "links": "Elizabeth line, Southeastern"},
    "Hounslow":              {"zone": "4-5", "links": "Piccadilly, District lines"},
    "Croydon":               {"zone": "5",   "links": "Tram, Thameslink, Southern"},
    "Waltham Forest":        {"zone": "3-4", "links": "Victoria line, Overground"},
    "Brent":                 {"zone": "3-4", "links": "Jubilee, Metropolitan, Bakerloo"},
    "Lewisham":              {"zone": "2-3", "links": "DLR, Southeastern"},
    "Newham":                {"zone": "3-4", "links": "Elizabeth line, DLR, Jubilee"},
    "Merton":                {"zone": "3-4", "links": "Northern line, Tram"},
    "Barking and Dagenham":  {"zone": "4-5", "links": "District, Hammersmith & City, c2c"},
    "Tower Hamlets":         {"zone": "2",   "links": "DLR, Central, District lines"},
    "Southwark":             {"zone": "1-2", "links": "Jubilee, Northern, Bakerloo"},
    "Haringey":              {"zone": "3-4", "links": "Piccadilly, Victoria lines"},
    "Lambeth":               {"zone": "1-2", "links": "Victoria, Jubilee, Northern"},
    "Islington":             {"zone": "1-2", "links": "Northern, Victoria, Metropolitan"},
    "Hackney":               {"zone": "2",   "links": "Overground, Victoria line"},
    "Hammersmith and Fulham":{"zone": "2",   "links": "Piccadilly, District, Hammersmith"},
    "Camden":                {"zone": "2",   "links": "Northern, Jubilee, Metropolitan"},
    "Kensington and Chelsea":{"zone": "1-2", "links": "District, Circle, Piccadilly"},
    "Westminster":           {"zone": "1",   "links": "Victoria, Jubilee, Bakerloo, Circle"},
    "City of London":        {"zone": "1",   "links": "Central, Circle, District, Metropolitan"},
}

# ── Colours ───────────────────────────────────────────────────────────────────
TIER_COLOURS = {
    "Excellent": "#2ecc71",
    "Good":      "#27ae60",
    "Moderate":  "#f39c12",
    "Elevated":  "#e67e22",
    "High Risk": "#e74c3c",
}

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_summary():
    df = pd.read_csv(SUMMARY_FILE)
    df["house_price"] = df["house_price_k"] * 1000
    df["zone"]        = df["borough"].map(lambda b: TRANSPORT.get(b, {}).get("zone", "N/A"))
    df["transport"]   = df["borough"].map(lambda b: TRANSPORT.get(b, {}).get("links", "N/A"))
    df["location"]    = df["outer_london"].map({True: "Outer London", False: "Inner London"})
    return df

@st.cache_data
def load_crimes():
    return pd.read_csv(CRIMES_FILE)

df      = load_summary()
crimes  = load_crimes()

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/London_coat_of_arms.svg/200px-London_coat_of_arms.svg.png", width=60)
st.sidebar.title("London Safety Analysis")
st.sidebar.markdown("*Data-driven borough safety for families*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "🗺️ Borough Map", "⚖️ Compare Boroughs", "👨‍👩‍👧 Family Finder", "📊 Power BI Dashboard"],
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data source:** [data.police.uk](https://data.police.uk)  \n"
    "**Period:** January 2024 – December 2025  \n"
    "**Records:** 753,904  \n"
    "**Boroughs:** 33"
)
st.sidebar.markdown("---")
st.sidebar.markdown("Built by **Kudzanayi Shepherd Mhlanga**")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":

    st.title("🏙️ London Borough Safety Analysis")
    st.markdown("**January 2024 – December 2025 | 753,904 crime records | 33 boroughs**")
    st.markdown("---")

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    safest = df[df["rank"] == 1].iloc[0]
    col1.metric("Safest Borough",    safest["borough"],        f"{safest['safety_score']:.0f}/100")
    col2.metric("Most Affordable",   df.loc[df["house_price"].idxmin(), "borough"],
                f"£{df['house_price'].min()/1000:.0f}k avg")
    col3.metric("Best for Families", df.loc[df["family_score"].idxmax(), "borough"],
                f"{df['family_score'].max():.0f}/100 family score")
    col4.metric("Boroughs Analysed", "33", "All London boroughs")

    st.markdown("---")

    # Rankings chart
    st.subheader("Borough Safety Rankings")
    display = df[df["borough"] != "City of London"].sort_values("safety_score", ascending=True)

    fig = px.bar(
        display,
        x="safety_score",
        y="borough",
        orientation="h",
        color="tier",
        color_discrete_map=TIER_COLOURS,
        text="safety_score",
        labels={"safety_score": "Safety Score (0–100)", "borough": ""},
        height=900,
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        showlegend=True,
        legend_title="Safety Tier",
        xaxis_range=[90, 102],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Full data table
    st.subheader("Full Borough Data")
    table = df[["rank","borough","safety_score","tier","family_score",
                "house_price_k","location","zone","transport"]].copy()
    table.columns = ["Rank","Borough","Safety Score","Tier","Family Score",
                     "Avg Price (£k)","Location","TfL Zone","Transport Links"]
    st.dataframe(
        table.style.background_gradient(subset=["Safety Score"], cmap="RdYlGn"),
        use_container_width=True,
        hide_index=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Borough Map":

    st.title("🗺️ London Safety Map")
    st.markdown("Borough safety scores plotted by location. Hover for details.")
    st.markdown("---")

    # Borough centroids
    CENTROIDS = {
        "Barking and Dagenham": (51.5362, 0.0798),   "Barnet": (51.6252, -0.1517),
        "Bexley": (51.4416, 0.1503),                  "Brent": (51.5673, -0.2713),
        "Bromley": (51.4039, 0.0198),                 "Camden": (51.5517, -0.1588),
        "City of London": (51.5155, -0.0922),          "Croydon": (51.3714, -0.0977),
        "Ealing": (51.5130, -0.3089),                 "Enfield": (51.6538, -0.0799),
        "Greenwich": (51.4892, 0.0648),               "Hackney": (51.5450, -0.0553),
        "Hammersmith and Fulham": (51.4927, -0.2339), "Haringey": (51.5906, -0.1111),
        "Harrow": (51.5836, -0.3464),                 "Havering": (51.5779, 0.2120),
        "Hillingdon": (51.5441, -0.4760),             "Hounslow": (51.4746, -0.3680),
        "Islington": (51.5465, -0.1058),              "Kensington and Chelsea": (51.4991, -0.1938),
        "Kingston upon Thames": (51.4085, -0.3064),   "Lambeth": (51.4571, -0.1231),
        "Lewisham": (51.4452, -0.0209),               "Merton": (51.4014, -0.1988),
        "Newham": (51.5077, 0.0469),                  "Redbridge": (51.5590, 0.0741),
        "Richmond upon Thames": (51.4479, -0.3260),   "Southwark": (51.5035, -0.0804),
        "Sutton": (51.3618, -0.1945),                 "Tower Hamlets": (51.5099, -0.0059),
        "Waltham Forest": (51.5908, -0.0134),         "Wandsworth": (51.4567, -0.1920),
        "Westminster": (51.4975, -0.1357),
    }

    map_df = df.copy()
    map_df["lat"] = map_df["borough"].map(lambda b: CENTROIDS.get(b, (0,0))[0])
    map_df["lon"] = map_df["borough"].map(lambda b: CENTROIDS.get(b, (0,0))[1])
    map_df["label"] = map_df.apply(
        lambda r: f"{r['borough']}<br>Safety: {r['safety_score']:.1f}<br>Tier: {r['tier']}<br>Avg Price: £{r['house_price_k']}k",
        axis=1
    )

    color_filter = st.selectbox("Colour map by:", ["Safety Score", "Family Score", "House Price (£k)"])
    col_map = {"Safety Score": "safety_score", "Family Score": "family_score", "House Price (£k)": "house_price_k"}
    chosen  = col_map[color_filter]

    fig = px.scatter_mapbox(
        map_df,
        lat="lat", lon="lon",
        color=chosen,
        size="safety_score",
        size_max=30,
        hover_name="borough",
        hover_data={"safety_score": True, "tier": True, "house_price_k": True,
                    "family_score": True, "lat": False, "lon": False},
        color_continuous_scale="RdYlGn",
        mapbox_style="carto-positron",
        zoom=9,
        center={"lat": 51.5074, "lon": -0.1278},
        height=650,
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    # Tier summary
    st.subheader("Boroughs by Tier")
    cols = st.columns(len(TIER_COLOURS))
    for i, (tier, colour) in enumerate(TIER_COLOURS.items()):
        boroughs_in_tier = df[df["tier"] == tier]["borough"].tolist()
        with cols[i]:
            st.markdown(f"**:{colour[1:]}[{tier}]**" if False else f"**{tier}**")
            st.markdown(f"*{len(boroughs_in_tier)} borough(s)*")
            for b in boroughs_in_tier:
                st.markdown(f"• {b}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — COMPARE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚖️ Compare Boroughs":

    st.title("⚖️ Compare Boroughs")
    st.markdown("Select up to 3 boroughs to compare side by side.")
    st.markdown("---")

    all_boroughs = sorted(df["borough"].tolist())
    selected = st.multiselect(
        "Choose boroughs to compare:",
        options=all_boroughs,
        default=["Bromley", "Sutton", "Barnet"],
        max_selections=3,
    )

    if not selected:
        st.info("Please select at least one borough above.")
        st.stop()

    sel_df = df[df["borough"].isin(selected)]

    # Metric cards
    cols = st.columns(len(selected))
    for i, (_, row) in enumerate(sel_df.iterrows()):
        with cols[i]:
            st.markdown(f"### {row['borough']}")
            st.metric("Safety Score", f"{row['safety_score']:.1f}/100")
            st.metric("Family Score", f"{row['family_score']:.1f}/100")
            st.metric("Avg House Price", f"£{row['house_price_k']}k")
            st.metric("Location", row["location"])
            st.metric("TfL Zone", row["zone"])
            st.markdown(f"**Transport:** {row['transport']}")
            st.markdown(f"**Tier:** `{row['tier']}`")

    st.markdown("---")

    # Radar chart comparison
    st.subheader("Head-to-Head Radar Chart")

    categories = ["Safety Score", "Family Score", "Affordability", "Transport Score"]

    max_price = df["house_price_k"].max()

    def transport_score(zone_str):
        try:
            low = int(str(zone_str).split("-")[0])
            return max(0, 100 - (low - 1) * 15)
        except:
            return 50

    fig = go.Figure()
    colours = ["#3498db", "#e74c3c", "#2ecc71"]
    for i, (_, row) in enumerate(sel_df.iterrows()):
        afford = round((1 - row["house_price_k"] / max_price) * 100, 1)
        trans  = transport_score(row["zone"])
        vals   = [row["safety_score"], row["family_score"], afford, trans]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=row["borough"],
            line_color=colours[i % len(colours)],
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Crime type breakdown
    st.markdown("---")
    st.subheader("Crime Type Breakdown")

    crime_sel = crimes[crimes["borough"].isin(selected)]
    crime_grp = crime_sel.groupby(["borough", "crime_type"])["count"].sum().reset_index()

    fig2 = px.bar(
        crime_grp,
        x="crime_type",
        y="count",
        color="borough",
        barmode="group",
        labels={"crime_type": "Crime Type", "count": "Total Crimes (2024–2025)"},
        height=450,
    )
    fig2.update_xaxes(tickangle=35)
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

    # Monthly trend
    st.markdown("---")
    st.subheader("Monthly Crime Trend")
    trend = crime_sel.groupby(["borough", "month"])["count"].sum().reset_index()
    fig3 = px.line(
        trend, x="month", y="count", color="borough",
        labels={"month": "Month", "count": "Total Crimes"},
        height=400,
        markers=True,
    )
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — FAMILY FINDER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👨‍👩‍👧 Family Finder":

    st.title("👨‍👩‍👧 Family Borough Finder")
    st.markdown("Tell us your priorities and we'll find the best London borough for your family.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Your Priorities")
        budget        = st.slider("Max house price budget (£k)", 300, 1700, 550, step=25)
        safety_weight = st.slider("How important is safety? (1–5)", 1, 5, 5)
        afford_weight = st.slider("How important is affordability? (1–5)", 1, 5, 4)
        transport_wt  = st.slider("How important is transport / commute? (1–5)", 1, 5, 3)
        outer_pref    = st.checkbox("Prefer Outer London (quieter, more space)", value=True)

    with col2:
        st.subheader("Filters")
        min_safety    = st.slider("Minimum safety score", 0, 100, 90)
        zone_max      = st.selectbox("Maximum TfL zone", ["Any", "2", "3", "4", "5", "6"], index=4)
        location_pref = st.radio("London area preference:", ["Any", "Outer London", "Inner London"])

    st.markdown("---")

    # Filter and score
    results = df.copy()

    # Budget filter
    results = results[results["house_price_k"] <= budget]

    # Safety filter
    results = results[results["safety_score"] >= min_safety]

    # Location filter
    if location_pref == "Outer London":
        results = results[results["outer_london"] == True]
    elif location_pref == "Inner London":
        results = results[results["outer_london"] == False]

    # Zone filter
    if zone_max != "Any":
        def min_zone(z):
            try: return int(str(z).split("-")[0])
            except: return 99
        results = results[results["zone"].apply(min_zone) <= int(zone_max)]

    if results.empty:
        st.warning("No boroughs match your filters. Try relaxing your budget or safety minimum.")
        st.stop()

    # Outer London bonus
    if outer_pref:
        results["outer_bonus"] = results["outer_london"].apply(lambda x: 10 if x else 0)
    else:
        results["outer_bonus"] = 0

    # Composite recommendation score
    max_price      = df["house_price_k"].max()
    afford_score   = (1 - results["house_price_k"] / max_price) * 100

    def transport_score(zone_str):
        try:
            low = int(str(zone_str).split("-")[0])
            return max(0, 100 - (low - 1) * 15)
        except:
            return 50

    t_scores = results["zone"].apply(transport_score)

    total_weight = safety_weight + afford_weight + transport_wt
    results["recommendation_score"] = (
        (results["safety_score"] * safety_weight / total_weight) +
        (afford_score            * afford_weight / total_weight) +
        (t_scores                * transport_wt  / total_weight) +
        results["outer_bonus"]
    ).round(1)

    results = results.sort_values("recommendation_score", ascending=False).head(10)

    # Display top picks
    st.subheader(f"Top {len(results)} Boroughs for Your Family")

    for i, (_, row) in enumerate(results.iterrows()):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"**{i+1}.**"
        with st.expander(f"{medal} {row['borough']} — Score: {row['recommendation_score']:.1f}/100", expanded=(i < 3)):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Safety Score",  f"{row['safety_score']:.1f}")
            c2.metric("House Price",   f"£{row['house_price_k']}k avg")
            c3.metric("TfL Zone",      row["zone"])
            c4.metric("Location",      row["location"])
            st.markdown(f"**Transport links:** {row['transport']}")
            st.markdown(f"**Safety tier:** `{row['tier']}`  |  **Family score:** {row['family_score']:.1f}/100")

    st.markdown("---")

    # Bar chart of results
    fig = px.bar(
        results.sort_values("recommendation_score"),
        x="recommendation_score",
        y="borough",
        orientation="h",
        color="recommendation_score",
        color_continuous_scale="RdYlGn",
        text="recommendation_score",
        labels={"recommendation_score": "Your Match Score", "borough": ""},
        height=400,
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "💡 **Tip:** These scores are based on 2024–2025 crime data, approximate house prices, "
        "and TfL zone estimates. Always visit a borough in person before making your decision!"
    )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — POWER BI DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Power BI Dashboard":

    st.title("📊 Power BI Dashboard")
    st.markdown("Full interactive Power BI report — crime trends, borough breakdowns, and safety analysis.")
    st.markdown("---")

    # ── Paste your Power BI embed URL here after publishing ──────────────────
    POWERBI_EMBED_URL = ""   # e.g. "https://app.powerbi.com/view?r=eyJ..."

    if not POWERBI_EMBED_URL:
        st.info(
            "**Power BI dashboard coming soon.**\n\n"
            "To connect your Power BI report:\n"
            "1. Open Power BI Desktop and build your report using the project CSV files\n"
            "2. Publish it to Power BI Service (app.powerbi.com)\n"
            "3. Go to File → Publish to web → copy the embed URL\n"
            "4. Paste the URL into `POWERBI_EMBED_URL` in `app.py`\n\n"
            "The dashboard will appear here automatically once the URL is set."
        )

        # Show a preview of what the Power BI report should contain
        st.markdown("### Suggested Power BI Report Pages")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Page 1 — Borough Overview**
            - Safety score bar chart (all 33 boroughs)
            - Tier breakdown donut chart
            - KPI cards: safest, most affordable, best family borough

            **Page 2 — Crime Analysis**
            - Crime type breakdown by borough
            - Monthly trend line (2024–2025)
            - Heatmap: borough vs crime type
            """)
        with col2:
            st.markdown("""
            **Page 3 — Family Suitability**
            - Family score vs house price scatter plot
            - Outer vs Inner London comparison
            - Top 10 family boroughs table

            **Page 4 — Map View**
            - Filled map of London boroughs
            - Colour-coded by safety score
            - Tooltip: score, tier, price, transport
            """)

        st.markdown("---")
        st.markdown("**Data files to use in Power BI:**")
        st.code(
            "data/processed/borough_safety_summary.csv\n"
            "data/raw/crime_data_summary.csv\n"
            "data/raw/borough_population.csv",
            language="text"
        )

    else:
        # Render the embedded Power BI report
        st.components.v1.iframe(
            POWERBI_EMBED_URL,
            height=700,
            scrolling=True,
        )
        st.caption(
            "Powered by Microsoft Power BI · Data: data.police.uk (Jan 2024 – Dec 2025)"
        )
