import streamlit as st
import pandas as pd
import requests
import sys
import os
from datetime import datetime

# ── Path setup ────────────────────────────────────────────────────────────────
script_path = os.path.join(os.path.dirname(__file__), "..", "script")
sys.path.insert(0, script_path)

from visualise import (
    load_data,
    choropleth_map,
    continent_trend,
    top_countries_chart,
    country_comparison,
    continent_violin,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global TB Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: #F0F4F8; }

    .hero-banner {
        background: linear-gradient(135deg, #1B2A4A 0%, #2E6DA4 60%, #3A9BC1 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem 1.6rem;
        margin-bottom: 1.5rem;
        color: white;
    }
    .hero-banner h1 {
        font-size: 2.2rem !important;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
        color: white !important;
    }
    .hero-banner p { font-size: 1rem; opacity: 0.85; margin: 0; }
    .refresh-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 20px;
        padding: 0.25rem 0.9rem;
        font-size: 0.8rem;
        margin-top: 0.7rem;
        color: rgba(255,255,255,0.9);
    }

    /* KPI cards */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 4px solid #2E6DA4;
    }
    [data-testid="metric-container"] label {
        font-size: 0.78rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700;
        color: #1B2A4A !important;
    }
    [data-testid="stMetricDelta"] { font-size: 0.85rem !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: white;
        border-radius: 12px;
        padding: 0.4rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        font-size: 0.9rem;
        color: #64748B;
    }
    .stTabs [aria-selected="true"] {
        background: #2E6DA4 !important;
        color: white !important;
    }

    /* Chart / section cards */
    .chart-card {
        background: white;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        margin-bottom: 1rem;
    }

    hr { border-color: #E2E8F0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Constants ─────────────────────────────────────────────────────────────────
FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tb_data_clean_updated.csv")
WHO_TB_URL = "https://ghoapi.azureedge.net/api/MDG_0000000020"
WHO_COUNTRY_URL = "https://ghoapi.azureedge.net/api/DIMENSION/COUNTRY/DimensionValues"


# ── WHO data fetch ─────────────────────────────────────────────────────────────
def fetch_and_save_who_data() -> None:
    tb_resp = requests.get(WHO_TB_URL, timeout=30)
    tb_resp.raise_for_status()
    df_raw = pd.DataFrame(tb_resp.json()["value"])

    country_resp = requests.get(WHO_COUNTRY_URL, timeout=30)
    country_resp.raise_for_status()
    country_df = pd.DataFrame(country_resp.json()["value"])[["Code", "Title"]]

    merged = df_raw.merge(country_df, left_on="SpatialDim", right_on="Code", how="left")
    clean = (
        merged[["ParentLocation", "SpatialDim", "TimeDimensionValue", "NumericValue", "Title"]]
        .rename(columns={
            "SpatialDim": "country_code",
            "ParentLocation": "continent",
            "TimeDimensionValue": "year",
            "NumericValue": "tb_incidence",
            "Title": "Country",
        })
        .dropna(subset=["continent"])
    )
    clean.to_csv(FILE_PATH, index=False)


# ── Cached data loader ─────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data() -> pd.DataFrame:
    return load_data(FILE_PATH)


# ── Session state ──────────────────────────────────────────────────────────────
if "last_refreshed" not in st.session_state:
    st.session_state.last_refreshed = None
if "refresh_error" not in st.session_state:
    st.session_state.refresh_error = None


# ── Hero banner ────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([3, 1])

with left_col:
    refresh_text = (
        f"⏱️ Last refreshed: {st.session_state.last_refreshed}"
        if st.session_state.last_refreshed
        else "⏱️ Showing cached data — click Refresh to pull the latest figures"
    )
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1>🦠 Global Tuberculosis Dashboard</h1>
            <p>WHO Global Health Observatory · TB Incidence per 100,000 Population · 2000–present</p>
            <span class="refresh-badge">{refresh_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        with st.spinner("Fetching latest data from WHO API…"):
            try:
                fetch_and_save_who_data()
                get_data.clear()
                st.session_state.last_refreshed = datetime.now().strftime("%d %b %Y at %H:%M:%S")
                st.session_state.refresh_error = None
                st.rerun()
            except Exception as exc:
                st.session_state.refresh_error = str(exc)

    if st.session_state.refresh_error:
        st.error(f"Refresh failed: {st.session_state.refresh_error}")


# ── Load data ─────────────────────────────────────────────────────────────────
df = get_data()
min_year = int(df["year"].min())
max_year = int(df["year"].max())


# ── KPI metrics ───────────────────────────────────────────────────────────────
latest_df = df[df["year"] == max_year]
highest_row = latest_df.loc[latest_df["tb_incidence"].idxmax()]
lowest_row = latest_df.loc[latest_df["tb_incidence"].idxmin()]
global_avg = latest_df["tb_incidence"].mean()
total_countries = latest_df["Country"].nunique()

prev_df = df[df["year"] == max_year - 1]
prev_avg = prev_df["tb_incidence"].mean() if not prev_df.empty else global_avg
avg_delta = global_avg - prev_avg

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Countries Tracked", f"{total_countries}")
k2.metric("Data Spanning", f"{min_year} – {max_year}")
k3.metric(
    f"Global Avg ({max_year})",
    f"{global_avg:.1f} per 100k",
    delta=f"{avg_delta:+.1f} vs {max_year - 1}",
    delta_color="inverse",
)
k4.metric(
    f"Highest Burden ({max_year})",
    highest_row["Country"],
    f"{highest_row['tb_incidence']:.0f} per 100k",
    delta_color="off",
)
k5.metric(
    f"Lowest Burden ({max_year})",
    lowest_row["Country"],
    f"{lowest_row['tb_incidence']:.1f} per 100k",
    delta_color="off",
)

# TB incidence explanation
st.info(
    "**What does 'per 100,000' mean?** TB Incidence measures how many new tuberculosis cases "
    "are diagnosed for every 100,000 people in a year. A value of **100** means roughly "
    "1 in every 1,000 people develops TB annually. A value of **500** means 1 in 200 people. "
    "For context, the UK typically sits below 10, while high-burden countries like South Africa "
    "can exceed 500."
)

st.markdown("<br>", unsafe_allow_html=True)


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_map, tab_trends, tab_rankings, tab_explorer, tab_data = st.tabs(
    ["🌍 Global Map", "📈 Trends", "🏆 Rankings", "🔍 Country Explorer", "📋 Data"]
)


# ─── Tab 1: Global Map ────────────────────────────────────────────────────────
with tab_map:
    map_year = st.slider(
        "Select year to display on map:",
        min_value=min_year,
        max_value=max_year,
        value=max_year,
        key="map_year",
    )

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(choropleth_map(df, map_year), use_container_width=True)
    st.caption("Hover over any country to see its TB incidence rate. Drag to pan, scroll to zoom.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### Continent Averages")
    continent_avgs = (
        df[df["year"] == map_year]
        .groupby("continent")["tb_incidence"]
        .mean()
        .sort_values(ascending=False)
    )
    cols = st.columns(len(continent_avgs))
    for col, (cont, val) in zip(cols, continent_avgs.items()):
        col.metric(cont, f"{val:.1f} per 100k")


# ─── Tab 2: Trends ────────────────────────────────────────────────────────────
with tab_trends:
    # ── Continent trend line ──────────────────────────────────────────────────
    all_continents = sorted(df["continent"].unique().tolist())
    selected_continents = st.multiselect(
        "Select continents to display:",
        options=all_continents,
        default=all_continents,
        key="trends_continents",
    )

    if not selected_continents:
        st.warning("Select at least one continent to display the trend chart.")
    else:
        df_trend = df[df["continent"].isin(selected_continents)]
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(continent_trend(df_trend, selected_continents), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── Distribution by continent ─────────────────────────────────────────────
    st.markdown("#### Distribution of TB Incidence by Continent")
    st.caption(
        "Each dot is a country. The box shows where the middle 50% of countries sit. "
        "The wider shape shows the full spread. Use the slider to explore different years."
    )
    violin_year = st.slider(
        "Select year for distribution chart:",
        min_value=min_year,
        max_value=max_year,
        value=max_year,
        key="violin_year",
    )
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(continent_violin(df, violin_year), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ─── Tab 3: Rankings ─────────────────────────────────────────────────────────
with tab_rankings:
    rc1, rc2 = st.columns(2)
    with rc1:
        year_range = st.slider(
            "Year range:",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="rankings_years",
        )
    with rc2:
        n_countries = st.select_slider(
            "Number of countries to show:",
            options=[5, 10, 15, 20],
            value=10,
            key="rankings_n",
        )

    st.caption(
        "Rankings show the average TB incidence per country across the selected year range. "
        "A higher average means TB has been consistently more prevalent over time."
    )

    bc1, bc2 = st.columns(2)
    with bc1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(
            top_countries_chart(df, year_range, n=n_countries, highest=True),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with bc2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(
            top_countries_chart(df, year_range, n=n_countries, highest=False),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ─── Tab 4: Country Explorer ─────────────────────────────────────────────────
with tab_explorer:
    all_countries = sorted(df["Country"].dropna().unique().tolist())
    candidates = ["India", "Nigeria", "South Africa", "China", "Brazil", "Indonesia"]
    defaults = [c for c in candidates if c in all_countries][:4]

    selected_countries = st.multiselect(
        "Select countries to compare:",
        options=all_countries,
        default=defaults,
        key="explorer_countries",
    )

    explorer_year_range = st.slider(
        "Year range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        key="explorer_years",
    )

    if selected_countries:
        df_explorer = df[
            (df["year"] >= explorer_year_range[0])
            & (df["year"] <= explorer_year_range[1])
        ]
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(
            country_comparison(df_explorer, selected_countries),
            use_container_width=True,
        )
        st.caption("Hover over any line to see the exact TB incidence value for that year.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Select at least one country above to display the chart.")


# ─── Tab 5: Data ─────────────────────────────────────────────────────────────
with tab_data:
    st.markdown("#### Raw Dataset")

    search = st.text_input("Search by country name:", placeholder="e.g. India")

    display_df = df.drop(columns=["country_code"]).rename(columns={
        "continent": "Continent",
        "year": "Year",
        "tb_incidence": "TB Incidence per 100,000",
        "Country": "Country",
    })

    if search:
        display_df = display_df[
            display_df["Country"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(
        display_df.sort_values(["Year", "TB Incidence per 100,000"], ascending=[False, False]),
        use_container_width=True,
        height=480,
    )
    st.caption(f"{len(display_df):,} rows shown. Source: WHO Global Health Observatory.")


# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center; color:#94A3B8; font-size:0.8rem;'>"
    "Data: WHO Global Health Observatory · "
    "Built with Streamlit &amp; Plotly · "
    "Click <strong>Refresh Data</strong> to pull the latest WHO figures"
    "</p>",
    unsafe_allow_html=True,
)
