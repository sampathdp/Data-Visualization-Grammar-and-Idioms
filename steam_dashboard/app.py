

import streamlit as st
import pandas as pd
import sys
import os

# Add directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from services.loader import load_raw_data, get_exploded_genre_df, get_unique_genres
from components.kpi_cards import render_kpi_row_compact
from components.charts import (
    render_market_timeline_compact,
    render_opportunity_scatter_compact,
    render_genre_year_heatmap_compact
)
from components.network import render_publisher_genre_platform_sankey_compact
from components.story_charts import (
    render_story_stage_1,
    render_story_stage_2_treemap,
    render_story_stage_4,
    render_story_stage_geospatial_map
)

st.set_page_config(
    page_title="Steam Market Visual Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Zero-Scroll CSS
st.markdown("""
<style>
    /* Completely hide default Streamlit header bar to prevent clipping */
    [data-testid="stHeader"] {
        display: none !important;
    }
    header {
        visibility: hidden !important;
    }
    
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0.2rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }
    
    .stApp {
        background-color: #F1F5F9;
        color: #0F172A;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Main App Light Theme Text */
    section.main p, 
    section.main label, 
    section.main span, 
    section.main [data-testid="stWidgetLabel"] p {
        color: #0F172A !important;
    }

    /* Sidebar High-Contrast Text & Controls */
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] label span,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    /* Slider values & numbers in Sidebar */
    section[data-testid="stSidebar"] [data-testid="stSliderTickBarMin"],
    section[data-testid="stSidebar"] [data-testid="stSliderTickBarMax"],
    section[data-testid="stSidebar"] div[data-testid="stThumbValue"],
    section[data-testid="stSidebar"] [data-baseweb="slider"] div {
        color: #F8FAFC !important;
        font-weight: 600 !important;
    }
    
    /* Number input and Multiselect text in Sidebar */
    section[data-testid="stSidebar"] input {
        color: #FFFFFF !important;
    }
    
    /* Top Header Bar Container */
    .top-header-container {
        background: #FFFFFF;
        border: 1.5px solid #CBD5E1;
        border-radius: 6px;
        padding: 6px 14px;
        margin-bottom: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    
    .app-title-text {
        font-size: 1.15rem;
        font-weight: 800;
        color: #0F172A !important;
        letter-spacing: -0.01em;
    }

    /* Radio Switcher Custom High-Contrast Styling */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 4px 10px !important;
        gap: 1.2rem !important;
        display: flex !important;
        align-items: center !important;
    }

    div[data-testid="stRadio"] label {
        margin: 0 !important;
        cursor: pointer !important;
    }

    div[data-testid="stRadio"] label p, 
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadio"] label div {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
    }

    /* 2x2 Grid Container Boxes */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-color: #CBD5E1 !important;
        border-radius: 6px !important;
        padding: 6px 10px !important;
        margin-bottom: 6px !important;
    }

    .viz-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #0F172A !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 2px;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 2px;
    }
    
    .viz-sub {
        font-size: 0.72rem;
        color: #334155 !important;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# 1. Load Data
df_raw = load_raw_data()
df_exploded = get_exploded_genre_df(df_raw)
available_genres = get_unique_genres(df_raw)

# 2. Top Header with Prominent 1-Click Dashboard Switcher
col_title, col_switch = st.columns([1.25, 1.0])

with col_title:
    st.markdown("""
    <div style="padding-top: 4px;">
        <span class="app-title-text">🎮 Steam Market Visual Intelligence Suite</span>
    </div>
    """, unsafe_allow_html=True)

with col_switch:
    selected_dashboard = st.radio(
        "Select Active Dashboard View:",
        options=["📊 1. Exploratory Explorer", "📖 2. Explanatory Story"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

# Dynamic Default Year Filter based on Active Dashboard
is_dashboard_2 = selected_dashboard and "2. Explanatory" in str(selected_dashboard)
current_dash_mode = "2. Explanatory" if is_dashboard_2 else "1. Exploratory"

if 'last_dash_mode' not in st.session_state:
    st.session_state['last_dash_mode'] = current_dash_mode
    st.session_state['year_slider_widget'] = (2005, 2024) if is_dashboard_2 else (2015, 2024)
elif st.session_state['last_dash_mode'] != current_dash_mode:
    st.session_state['last_dash_mode'] = current_dash_mode
    st.session_state['year_slider_widget'] = (2005, 2024) if is_dashboard_2 else (2015, 2024)

# 3. Sidebar Filters
with st.sidebar:
    st.markdown("### Filters")
        
    min_yr = int(df_raw['release_year'].min()) if not df_raw['release_year'].isna().all() else 2000
    max_yr = int(df_raw['release_year'].max()) if not df_raw['release_year'].isna().all() else 2024
    
    selected_years = st.slider(
        "Release Year Window",
        min_value=min_yr,
        max_value=max_yr,
        key="year_slider_widget"
    )

    selected_genres = st.multiselect(
        "Product Genres",
        options=available_genres,
        default=['Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 'Casual', 'Indie']
    )

    selected_price = st.slider("Price Ceiling ($ USD)", min_value=0.0, max_value=70.0, value=60.0, step=5.0)
    min_reviews = st.number_input("Min Evidence (Reviews)", min_value=0, max_value=500, value=20, step=10)

# Filter Data
df_filtered = df_raw[
    (df_raw['release_year'] >= selected_years[0]) & 
    (df_raw['release_year'] <= selected_years[1]) &
    (df_raw['price_usd'].fillna(0) <= selected_price) &
    (df_raw['overall_review_count'] >= min_reviews)
].copy()

if selected_genres:
    df_filtered = df_filtered[df_filtered['genres_list'].apply(lambda gl: any(g in selected_genres for g in gl) if isinstance(gl, list) else False)]

df_exp_filtered = df_exploded[
    (df_exploded['release_year'] >= selected_years[0]) & 
    (df_exploded['release_year'] <= selected_years[1]) &
    (df_exploded['genre'].isin(selected_genres if selected_genres else available_genres)) &
    (df_exploded['price_usd'].fillna(0) <= selected_price) &
    (df_exploded['overall_review_count'] >= min_reviews)
]

# =========================================================================
#  DASHBOARD 1: EXPLORATORY MARKET INTELLIGENCE EXPLORER
# =========================================================================
if selected_dashboard is None or "1. Exploratory" in str(selected_dashboard):
    render_kpi_row_compact(df_filtered)
    st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown('<div class="viz-label">1. Temporal Trajectory: Releases by Genre</div>', unsafe_allow_html=True)
            fig_time = render_market_timeline_compact(df_exp_filtered, selected_genres if selected_genres else available_genres[:5])
            st.plotly_chart(fig_time, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown('<div class="viz-label">2. Commercial Matrix: Pricing vs. Positivity %</div>', unsafe_allow_html=True)
            fig_scatter = render_opportunity_scatter_compact(df_filtered)
            st.plotly_chart(fig_scatter, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        with st.container(border=True):
            st.markdown('<div class="viz-label">3. Cross-Tab Heatmap: Year × Genre Positivity %</div>', unsafe_allow_html=True)
            fig_heat = render_genre_year_heatmap_compact(df_exp_filtered, selected_genres if selected_genres else available_genres[:6], min_year=selected_years[0])
            st.plotly_chart(fig_heat, use_container_width=True)

    with col4:
        with st.container(border=True):
            st.markdown('<div class="viz-label">4. Network Structure: Publisher → Genre → Platform</div>', unsafe_allow_html=True)
            fig_sankey = render_publisher_genre_platform_sankey_compact(df_filtered, max_publishers=6)
            if fig_sankey:
                st.plotly_chart(fig_sankey, use_container_width=True)

# =========================================================================
#  DASHBOARD 2: EXPLANATORY MARKET EVOLUTION STORY
# =========================================================================
else:
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("""
                <div class="viz-label">1. Platform Deregulation Caused an Exponential Supply Surge</div>
                <div class="viz-sub"><b>Temporal Insight:</b> 2012 Greenlight & 2017 Direct expanded catalog from 500 to 8,000+ games/yr.</div>
            """, unsafe_allow_html=True)
            fig1 = render_story_stage_1(df_filtered)
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown("""
                <div class="viz-label">2. Market Share Treemap (Area = Titles N, Color = Positivity %)</div>
                <div class="viz-sub"><b>Categorical Insight:</b> Indie & Action dominate volume; RPG & Simulation achieve peak satisfaction.</div>
            """, unsafe_allow_html=True)
            fig2 = render_story_stage_2_treemap(df_exp_filtered)
            st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        with st.container(border=True):
            st.markdown("""
                <div class="viz-label">3. The Small-Sample Illusion (100% Rating Trap)</div>
                <div class="viz-sub"><b>Statistical Insight:</b> 100% positivity with N ≤ 5 reviews is high risk; always enforce N ≥ 100 evidence floor.</div>
            """, unsafe_allow_html=True)
            fig3 = render_story_stage_4(df_filtered)
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        with st.container(border=True):
            st.markdown("""
                <div class="viz-label">4. Global Game Development & Studio Production Map</div>
                <div class="viz-sub"><b>Geospatial Insight:</b> North America, Western Europe, and East Asia form dominant production epicenters.</div>
            """, unsafe_allow_html=True)
            fig4 = render_story_stage_geospatial_map(df_filtered)
            st.plotly_chart(fig4, use_container_width=True)

