"""
High-Contrast Academic Tableau Visualizations for Steam Market Intelligence.
Guarantees 100% visible, crystal-clear labels, axes, legends, and ticks on all display modes.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

TABLEAU_10 = {
    'Action': '#E15759',      # Red
    'Adventure': '#F28E2B',   # Orange
    'RPG': '#9C755F',         # Brown / Purple
    'Strategy': '#EDC948',    # Gold / Yellow
    'Simulation': '#59A14F',  # Green
    'Casual': '#76B7B2',      # Cyan
    'Indie': '#4E79A7',       # Blue
    'Sports': '#FF9DA7',      # Pink
    'Racing': '#B07AA1',      # Purple
    'Massively Multiplayer': '#868E96', # Slate
    'Other': '#64748B'
}

TEXT_COLOR = "#0F172A"       # Deep high-contrast Slate Navy
AXIS_COLOR = "#334155"       # Strong dark gray for axes
GRID_COLOR = "#E2E8F0"       # Subtle gridline

def render_market_timeline_compact(df_exploded: pd.DataFrame, top_genres: list):
    """
    1. Temporal Trajectory: Annual Releases by Genre.
    """
    df_chart = df_exploded[df_exploded['genre'].isin(top_genres)].copy()
    agg = df_chart.groupby(['release_year', 'genre'])['app_id'].nunique().reset_index()
    agg.rename(columns={'app_id': 'title_count', 'release_year': 'Year', 'genre': 'Genre'}, inplace=True)
    agg = agg.sort_values('Year')

    fig = px.area(
        agg,
        x='Year',
        y='title_count',
        color='Genre',
        color_discrete_map=TABLEAU_10,
        labels={'title_count': 'Catalog Volume (N)', 'Year': 'Release Year'},
        template="plotly_white",
        height=270
    )
    
    fig.update_layout(
        font=dict(family="Segoe UI, Arial, sans-serif", size=11, color=TEXT_COLOR),
        margin=dict(l=40, r=15, t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            title=None,
            font=dict(size=10, color=TEXT_COLOR)
        ),
        xaxis=dict(
            dtick=1,
            gridcolor=GRID_COLOR,
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(size=10, color=TEXT_COLOR, family="Segoe UI, Arial"),
            title=dict(text="Release Year", font=dict(size=11, color=TEXT_COLOR))
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(size=10, color=TEXT_COLOR, family="Segoe UI, Arial"),
            title=dict(text="Titles (N)", font=dict(size=11, color=TEXT_COLOR))
        ),
        hovermode="x unified",
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF'
    )
    return fig


def render_opportunity_scatter_compact(df: pd.DataFrame):
    """
    2. Commercial Matrix: Pricing vs. Positivity %.
    """
    df_valid = df.dropna(subset=['overall_review_%', 'price_usd']).copy()
    
    agg = df_valid.groupby('primary_genre').agg(
        app_count=('app_id', 'nunique'),
        median_price=('price_usd', 'median'),
        median_positivity=('overall_review_%', 'median'),
        total_reviews=('overall_review_count', 'sum')
    ).reset_index()
    
    agg['bubble_size'] = np.sqrt(agg['total_reviews']) + 12

    fig = px.scatter(
        agg,
        x='median_price',
        y='median_positivity',
        size='bubble_size',
        color='primary_genre',
        color_discrete_map=TABLEAU_10,
        text='primary_genre',
        hover_name='primary_genre',
        hover_data={'median_price': ':.2f', 'median_positivity': ':.1f', 'app_count': True, 'bubble_size': False},
        labels={'median_price': 'Median Price ($ USD)', 'median_positivity': 'Review Positivity (%)'},
        template="plotly_white",
        height=270
    )

    fig.update_traces(
        textposition='top center',
        textfont=dict(size=10, color=TEXT_COLOR, family="Segoe UI, Arial")
    )

    # Reference Benchmarks
    fig.add_hline(y=75, line_dash="dash", line_color="#64748B", annotation_text="Benchmark (75%)", annotation_position="top right", annotation_font=dict(size=9, color=TEXT_COLOR))
    fig.add_vline(x=10, line_dash="dash", line_color="#64748B", annotation_text="Mid-tier ($10)", annotation_position="top left", annotation_font=dict(size=9, color=TEXT_COLOR))

    fig.update_layout(
        font=dict(family="Segoe UI, Arial, sans-serif", size=11, color=TEXT_COLOR),
        margin=dict(l=40, r=15, t=15, b=30),
        showlegend=False,
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        xaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(size=10, color=TEXT_COLOR),
            title=dict(text="Median Price ($ USD)", font=dict(size=11, color=TEXT_COLOR))
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            range=[60, 95],
            tickfont=dict(size=10, color=TEXT_COLOR),
            title=dict(text="Median Positivity (%)", font=dict(size=11, color=TEXT_COLOR))
        )
    )
    return fig


def render_genre_year_heatmap_compact(df_exploded: pd.DataFrame, top_genres: list, min_year: int = 2015):
    """
    3. Cross-Tab Heatmap: Year × Genre Positivity %.
    """
    df_chart = df_exploded[
        (df_exploded['genre'].isin(top_genres[:6])) & 
        (df_exploded['release_year'] >= min_year) &
        (df_exploded['overall_review_%'].notna())
    ].copy()

    agg = df_chart.groupby(['genre', 'release_year']).agg(
        median_positivity=('overall_review_%', 'median'),
        game_count=('app_id', 'nunique'),
        median_price=('price_usd', 'median')
    ).reset_index()

    pivot_pos = agg.pivot(index='genre', columns='release_year', values='median_positivity')
    pivot_cnt = agg.pivot(index='genre', columns='release_year', values='game_count').fillna(0)

    hover_text = []
    text_labels = []
    for g_idx, genre in enumerate(pivot_pos.index):
        row_hover = []
        row_lbl = []
        for y_idx, year in enumerate(pivot_pos.columns):
            pos = pivot_pos.iloc[g_idx, y_idx]
            n = pivot_cnt.iloc[g_idx, y_idx]
            if pd.isna(pos):
                row_hover.append("No Data")
                row_lbl.append("")
            else:
                row_hover.append(f"<b>{genre} ({year})</b><br>Positivity: <b>{pos:.1f}%</b><br>Titles: <b>{int(n):,}</b>")
                row_lbl.append(f"{pos:.0f}%")
        hover_text.append(row_hover)
        text_labels.append(row_lbl)

    fig = go.Figure(data=go.Heatmap(
        z=pivot_pos.values,
        x=[str(int(y)) for y in pivot_pos.columns],
        y=pivot_pos.index,
        colorscale="Blues",
        zmin=65,
        zmax=88,
        text=text_labels,
        texttemplate="%{text}",
        textfont=dict(size=10, color="#FFFFFF", family="Segoe UI, Arial"),
        colorbar=dict(
            title=dict(text="Pos %", font=dict(size=10, color=TEXT_COLOR)),
            thickness=12,
            tickfont=dict(size=9, color=TEXT_COLOR)
        ),
        hoverinfo="text",
        hovertext=hover_text
    ))

    fig.update_layout(
        font=dict(family="Segoe UI, Arial, sans-serif", size=11, color=TEXT_COLOR),
        template="plotly_white",
        height=260,
        margin=dict(l=60, r=15, t=15, b=25),
        xaxis=dict(
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(size=10, color=TEXT_COLOR),
            title=dict(text="Release Year", font=dict(size=11, color=TEXT_COLOR))
        ),
        yaxis=dict(
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(size=10, color=TEXT_COLOR),
            title=None
        ),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF'
    )
    return fig
