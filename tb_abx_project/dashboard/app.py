import streamlit as st
import pandas as pd
import sys
import os 


script_path = os.path.join(os.path.dirname(__file__), '..', 'script')
sys.path.insert(0, script_path)

from visualise import read_cvs, continent_graph, top_highest, top_lowest

# page configuration

st.set_page_config(
    page_title="Live Global Tuberculosis Incidence Dashbaord",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for bettter styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    h1 {
        color: #2C3E50;
        font-size: 3rem !important;
        margin-bottom: 1rem;
    }
    h2 {
        color: #34495E;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True) 

# Title
st.title("🏥 Global Tuberculosis Incidence Dashboard")

# Add a subtitle
st.markdown("### Tracking Tuberculosis Trends Worldwide (2000-2024)")

st.divider()

file_path = os.path.join(os.path.dirname(__file__),'..', 'data', 'tb_data_clean_updated.csv')

df = read_cvs(file_path)



# continent data 
st.header("Tuberculosis Incidence Trends by Continent")
continents_available = df['continent'].unique().tolist()
selected_continents = st.multiselect(
    "Select or remove continents to display:",
    options=continents_available,
    default=continents_available
)

if selected_continents:
    df_filtered = df[df["continent"].isin(selected_continents)]

    graph_continent = continent_graph(df_filtered)
    st.pyplot(graph_continent)
else: 
    st.warning("Please select at least 1 continent to display")

# top 10 highest countries 
st.header("Top 10 Countries with the Highest Tuberculosis Incidence")

#year range
min_year_highest = df['year'].min()
max_year_highest = df['year'].max()

selected_years_highest = st.slider(
    "Select year range:",
    min_value=min_year_highest,
    max_value=max_year_highest,
    value=(min_year_highest, max_year_highest),
    key="highest_years"

)

# filter the data by selected years
df_filtered_years_highest = df[(df['year'] >= selected_years_highest[0]) & (df['year'] <= selected_years_highest[1])]

top_high = top_highest(df_filtered_years_highest)
st.pyplot(top_high)

# top 10 lowest countries 
st.header("Top 10 Countries with the Lowest Tuberculosis Incidence")

min_year_lowest = df['year'].min()
max_year_lowest = df['year'].max()

selected_years_lowest = st.slider(
    "Select year range:",
    min_value=min_year_lowest,
    max_value=max_year_lowest,
    value=(min_year_lowest, max_year_highest),
    key="lowest_years"
)

df_filtered_years_lowest = df[(df['year'] >= selected_years_lowest[0]) & (df['year'] >= selected_years_lowest[1])]

top_low = top_lowest(df_filtered_years_lowest)
st.pyplot(top_low) 

