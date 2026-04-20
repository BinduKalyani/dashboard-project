import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="World Development Dashboard", layout="wide")

st.title("World Development Dashboard")
st.markdown("Explore global trends in life expectancy, GDP, and population across countries and years.")

df = px.data.gapminder()

st.sidebar.header("Filters")

continents = sorted(df["continent"].unique().tolist())
selected_continents = st.sidebar.multiselect(
    "Select Continents",
    options=continents,
    default=continents,
)

years = sorted(df["year"].unique().tolist())
selected_year = st.sidebar.select_slider(
    "Select Year",
    options=years,
    value=2007,
)

min_pop, max_pop = int(df["pop"].min()), int(df["pop"].max())
pop_range = st.sidebar.slider(
    "Population Range (millions)",
    min_value=0,
    max_value=int(max_pop / 1_000_000),
    value=(0, int(max_pop / 1_000_000)),
    step=10,
)

filtered = df[
    (df["year"] == selected_year)
    & (df["continent"].isin(selected_continents))
    & (df["pop"] >= pop_range[0] * 1_000_000)
    & (df["pop"] <= pop_range[1] * 1_000_000)
]

col1, col2, col3 = st.columns(3)
col1.metric("Countries Shown", len(filtered))
col2.metric("Avg Life Expectancy", f"{filtered['lifeExp'].mean():.1f} yrs" if not filtered.empty else "—")
col3.metric("Avg GDP per Capita", f"${filtered['gdpPercap'].mean():,.0f}" if not filtered.empty else "—")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Life Expectancy vs. GDP per Capita")
    if filtered.empty:
        st.info("No data matches the current filters.")
    else:
        fig_scatter = px.scatter(
            filtered,
            x="gdpPercap",
            y="lifeExp",
            size="pop",
            color="continent",
            hover_name="country",
            log_x=True,
            size_max=55,
            labels={
                "gdpPercap": "GDP per Capita (USD, log scale)",
                "lifeExp": "Life Expectancy (years)",
                "pop": "Population",
                "continent": "Continent",
            },
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_scatter.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif", size=13),
            legend=dict(title="Continent", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=20, t=20, b=40),
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with col_right:
    st.subheader("Top 15 Countries by GDP per Capita")
    if filtered.empty:
        st.info("No data matches the current filters.")
    else:
        top15 = filtered.nlargest(15, "gdpPercap").sort_values("gdpPercap")
        fig_bar = px.bar(
            top15,
            x="gdpPercap",
            y="country",
            orientation="h",
            color="continent",
            labels={
                "gdpPercap": "GDP per Capita (USD)",
                "country": "Country",
                "continent": "Continent",
            },
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_bar.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif", size=13),
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=40),
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.subheader("Life Expectancy Over Time by Continent")

continent_trend = (
    df[df["continent"].isin(selected_continents)]
    .groupby(["year", "continent"], as_index=False)["lifeExp"]
    .mean()
)

fig_line = px.line(
    continent_trend,
    x="year",
    y="lifeExp",
    color="continent",
    markers=True,
    labels={
        "year": "Year",
        "lifeExp": "Average Life Expectancy (years)",
        "continent": "Continent",
    },
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig_line.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Inter, sans-serif", size=13),
    legend=dict(title="Continent", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=20, t=20, b=40),
    xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
)
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")
with st.expander("View Raw Data"):
    st.dataframe(
        filtered[["country", "continent", "year", "lifeExp", "gdpPercap", "pop"]]
        .rename(columns={
            "country": "Country",
            "continent": "Continent",
            "year": "Year",
            "lifeExp": "Life Expectancy",
            "gdpPercap": "GDP per Capita",
            "pop": "Population",
        })
        .reset_index(drop=True),
        use_container_width=True,
    )

st.caption("Data source: Gapminder · Visualized with Plotly & Streamlit")
