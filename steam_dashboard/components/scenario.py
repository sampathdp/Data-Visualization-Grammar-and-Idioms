
import sys
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

try:
    from services.semantic_metrics import run_what_if_benchmark, calculate_saturation_index
except ImportError:
    from steam_dashboard.services.semantic_metrics import run_what_if_benchmark, calculate_saturation_index

def render_what_if_simulator(df_full):
    """
    Renders clean Tableau-style scenario simulator.
    """
    with st.expander("🎲 **What-If Game Launch Historical Scenario Benchmarker** (Click to Expand / Configure)", expanded=False):
        st.caption(
            "Methodological Notice: Evaluates proposed game parameters against historical cohorts. "
            "Decision support benchmark — not a predictive forecasting model."
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            proposed_genre = st.selectbox("Primary Genre", options=['Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 'Casual', 'Indie'], index=2)
            proposed_price = st.slider("Target Retail Price ($ USD)", min_value=0.0, max_value=70.0, value=24.99, step=1.0)
        with col2:
            target_platforms = st.multiselect("OS Platforms", options=['Windows', 'Mac', 'Linux'], default=['Windows', 'Mac'])
            min_reviews = st.number_input("Evidence Threshold (Min Reviews)", min_value=0, max_value=500, value=25, step=5)
        with col3:
            year_range = st.slider("Historical Window", min_value=2010, max_value=2024, value=(2018, 2024))

        benchmark = run_what_if_benchmark(
            df=df_full,
            genre=proposed_genre,
            target_price=proposed_price,
            platforms=target_platforms,
            year_range=year_range,
            min_reviews=min_reviews
        )
        saturation = calculate_saturation_index(df_full, proposed_genre, year_range)

        if benchmark['sample_size'] == 0:
            st.warning("No historical titles match this exact configuration.")
            return

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric("Comparable Titles (N)", f"{benchmark['sample_size']:,}")
        mcol2.metric("Cohort Median Positivity", f"{benchmark['median_positivity']:.1f}%")
        mcol3.metric("Price Percentile", f"{benchmark['price_percentile']:.1f}th")
        mcol4.metric("Market Saturation", f"{saturation['genre_share_%']:.1f}% ({saturation['saturation_rating']})")

        # Distribution Chart
        cohort_df = df_full[
            (df_full['release_year'] >= year_range[0]) & 
            (df_full['release_year'] <= year_range[1]) &
            (df_full['overall_review_count'] >= min_reviews) &
            (df_full['primary_genre'] == proposed_genre)
        ]
        
        if not cohort_df.empty:
            fig_hist = px.histogram(
                cohort_df,
                x='overall_review_%',
                nbins=20,
                template="plotly_white",
                color_discrete_sequence=['#4E79A7'],
                labels={'overall_review_%': 'Positivity (%)'}
            )
            fig_hist.add_vline(x=benchmark['median_positivity'], line_dash="dot", line_color="#E15759", annotation_text=f"Median ({benchmark['median_positivity']:.1f}%)")
            fig_hist.update_layout(
                font=dict(family="Segoe UI, -apple-system, Arial, sans-serif", size=10, color="#334155"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=220,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,0.9)'
            )
            st.plotly_chart(fig_hist, use_container_width=True)
