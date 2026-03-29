import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ── Colour palette used across all charts ──────────────────────────────────
CONTINENT_COLOURS = px.colors.qualitative.Set2
RED_SCALE = "Reds"
BLUE_SCALE = "Blues"
TRANSPARENT = "rgba(0,0,0,0)"
GRID_COLOUR = "rgba(180,180,180,0.2)"


def _base_layout(fig: go.Figure, height: int = 450) -> go.Figure:
    """Apply consistent transparent background and grid styling."""
    fig.update_layout(
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        height=height,
        font=dict(family="Inter, sans-serif", size=13, color="#1B2A4A"),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


# ── Data loading ───────────────────────────────────────────────────────────

def load_data(file_path: str) -> pd.DataFrame:
    """Load and lightly clean the TB CSV data."""
    df = pd.read_csv(file_path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["tb_incidence"] = pd.to_numeric(df["tb_incidence"], errors="coerce")
    df = df.dropna(subset=["tb_incidence", "year", "continent"])
    df["year"] = df["year"].astype(int)
    return df


# ── Charts ─────────────────────────────────────────────────────────────────

def choropleth_map(df: pd.DataFrame, selected_year: int) -> go.Figure:
    """World choropleth map for a single year."""
    year_df = df[df["year"] == selected_year].copy()
    cap = year_df["tb_incidence"].quantile(0.95)

    fig = px.choropleth(
        year_df,
        locations="country_code",
        color="tb_incidence",
        hover_name="Country",
        hover_data={
            "country_code": False,
            "tb_incidence": ":.1f",
            "continent": True,
        },
        color_continuous_scale=RED_SCALE,
        range_color=[0, cap],
        labels={"tb_incidence": "TB Incidence (per 100k)", "continent": "Continent"},
        title=f"TB Incidence Rate per 100,000 Population — {selected_year}",
    )
    fig.update_geos(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="rgba(100,100,100,0.4)",
        showland=True,
        landcolor="rgba(240,240,240,1)",
        showocean=True,
        oceancolor="rgba(210,230,255,1)",
        projection_type="natural earth",
    )
    fig.update_layout(
        coloraxis_colorbar=dict(title="per 100k", thickness=14),
        geo=dict(bgcolor=TRANSPARENT),
        margin=dict(l=0, r=0, t=50, b=0),
        height=520,
        paper_bgcolor=TRANSPARENT,
        font=dict(family="Inter, sans-serif", size=13, color="#1B2A4A"),
    )
    return fig


def continent_trend(df: pd.DataFrame, selected_continents: list) -> go.Figure:
    """Average TB incidence trend lines per continent."""
    df_f = df[df["continent"].isin(selected_continents)]
    yearly = df_f.groupby(["year", "continent"])["tb_incidence"].mean().reset_index()

    fig = px.line(
        yearly,
        x="year",
        y="tb_incidence",
        color="continent",
        markers=True,
        title="Average TB Incidence by Continent Over Time",
        labels={
            "tb_incidence": "Avg TB Incidence (per 100k)",
            "year": "Year",
            "continent": "Continent",
        },
        color_discrete_sequence=CONTINENT_COLOURS,
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=5))
    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOUR),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOUR, title="Avg Incidence (per 100k)"),
    )
    _base_layout(fig)
    return fig


def continent_heatmap(df: pd.DataFrame) -> go.Figure:
    """Year × continent average incidence heatmap."""
    pivot = (
        df.groupby(["year", "continent"])["tb_incidence"]
        .mean()
        .reset_index()
        .pivot(index="continent", columns="year", values="tb_incidence")
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=RED_SCALE,
            text=pivot.values.round(0),
            texttemplate="%{text:.0f}",
            hovertemplate="Year: %{x}<br>Continent: %{y}<br>Avg: %{z:.1f} per 100k<extra></extra>",
            colorbar=dict(title="per 100k", thickness=14),
        )
    )
    fig.update_layout(
        title="TB Incidence Heatmap: Continent × Year",
        xaxis_title="Year",
        yaxis_title="",
    )
    _base_layout(fig, height=380)
    return fig


def top_countries_chart(
    df: pd.DataFrame,
    year_range: tuple,
    n: int = 10,
    highest: bool = True,
) -> go.Figure:
    """Horizontal bar chart for top-N highest or lowest countries."""
    df_yr = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
    countries = df_yr.groupby(["Country", "continent"])["tb_incidence"].mean().reset_index()

    if highest:
        top_n = countries.nlargest(n, "tb_incidence").sort_values("tb_incidence")
        title = f"Top {n} Highest — {year_range[0]}–{year_range[1]}"
        scale = RED_SCALE
    else:
        top_n = countries.nsmallest(n, "tb_incidence").sort_values("tb_incidence", ascending=False)
        title = f"Top {n} Lowest — {year_range[0]}–{year_range[1]}"
        scale = BLUE_SCALE

    fig = px.bar(
        top_n,
        x="tb_incidence",
        y="Country",
        orientation="h",
        color="tb_incidence",
        color_continuous_scale=scale,
        text=top_n["tb_incidence"].round(0),
        hover_data={"continent": True, "tb_incidence": ":.1f"},
        title=title,
        labels={"tb_incidence": "Avg TB Incidence (per 100k)", "Country": ""},
    )
    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOUR),
        yaxis=dict(showgrid=False),
    )
    _base_layout(fig, height=420)
    return fig


def country_comparison(df: pd.DataFrame, selected_countries: list) -> go.Figure:
    """Multi-line chart for comparing selected countries over time."""
    df_f = df[df["Country"].isin(selected_countries)]

    fig = px.line(
        df_f,
        x="year",
        y="tb_incidence",
        color="Country",
        title="TB Incidence Trends — Country Comparison",
        labels={"tb_incidence": "TB Incidence per 100,000", "year": "Year"},
    )
    fig.update_traces(line=dict(width=2.5))
    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOUR),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOUR),
    )
    _base_layout(fig)
    return fig


def continent_violin(df: pd.DataFrame, selected_year: int) -> go.Figure:
    """Violin + box plot showing the spread of TB incidence across continents."""
    year_df = df[df["year"] == selected_year]

    fig = px.violin(
        year_df,
        x="continent",
        y="tb_incidence",
        box=True,
        points="all",
        color="continent",
        title=f"Distribution of TB Incidence by Continent — {selected_year}",
        labels={"tb_incidence": "TB Incidence (per 100k)", "continent": ""},
        color_discrete_sequence=CONTINENT_COLOURS,
        hover_data=["Country"],
    )
    fig.update_layout(
        showlegend=False,
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOUR),
        xaxis=dict(showgrid=False),
    )
    _base_layout(fig)
    return fig
