"""
High-Contrast Compact Sankey Diagram for Steam Market Intelligence.
Guarantees 100% visible, crisp node and link text.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def render_publisher_genre_platform_sankey_compact(df: pd.DataFrame, max_publishers: int = 6):
    """
    Compact Tableau-style Sankey Diagram with crisp, high-contrast labels.
    """
    df_valid = df.dropna(subset=['publisher', 'primary_genre']).copy()
    df_valid = df_valid[~df_valid['publisher'].isin(['Self-Published / Unknown', 'Unknown Developer', 'None'])]

    top_publishers = df_valid['publisher'].value_counts().head(max_publishers).index.tolist()
    df_sankey = df_valid[df_valid['publisher'].isin(top_publishers)].copy()

    if df_sankey.empty:
        return None

    # L1: Publisher -> Genre
    l1 = df_sankey.groupby(['publisher', 'primary_genre'])['app_id'].nunique().reset_index()
    l1.columns = ['source', 'target', 'value']

    # L2: Genre -> Platform
    platform_rows = []
    for _, row in df_sankey.iterrows():
        g = row['primary_genre']
        if row['win_support']: platform_rows.append((g, 'Win OS', row['app_id']))
        if row['mac_support']: platform_rows.append((g, 'Mac OS', row['app_id']))
        if row['linux_support']: platform_rows.append((g, 'Linux OS', row['app_id']))
    
    df_plat = pd.DataFrame(platform_rows, columns=['genre', 'platform', 'app_id'])
    l2 = df_plat.groupby(['genre', 'platform'])['app_id'].nunique().reset_index()
    l2.columns = ['source', 'target', 'value']

    all_publishers = sorted(l1['source'].unique().tolist())
    all_genres = sorted(list(set(l1['target'].unique().tolist() + l2['source'].unique().tolist())))
    all_platforms = sorted(l2['target'].unique().tolist())

    nodes = all_publishers + all_genres + all_platforms
    node_to_idx = {name: idx for idx, name in enumerate(nodes)}

    node_colors = []
    for n in nodes:
        if n in all_publishers:
            node_colors.append('#4E79A7')  # Blue
        elif n in all_genres:
            node_colors.append('#E15759')  # Red
        else:
            node_colors.append('#59A14F')  # Green

    sources, targets, values, link_hover = [], [], [], []

    for _, row in l1.iterrows():
        sources.append(node_to_idx[row['source']])
        targets.append(node_to_idx[row['target']])
        values.append(row['value'])
        link_hover.append(f"{row['source']} → {row['target']}: {row['value']} titles")

    for _, row in l2.iterrows():
        sources.append(node_to_idx[row['source']])
        targets.append(node_to_idx[row['target']])
        values.append(row['value'])
        link_hover.append(f"{row['source']} → {row['target']}: {row['value']} titles")

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=12,
            thickness=14,
            line=dict(color="#1E293B", width=0.8),
            label=nodes,
            color=node_colors,
            hovertemplate='Node: <b>%{label}</b><br>Volume: %{value} titles<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color='rgba(148, 163, 184, 0.35)',
            customdata=link_hover,
            hovertemplate='%{customdata}<extra></extra>'
        )
    )])

    fig.update_layout(
        font=dict(family="Segoe UI, Arial, sans-serif", size=10.5, color="#0F172A"),
        template="plotly_white",
        height=260,
        margin=dict(l=10, r=10, t=15, b=15),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF'
    )
    return fig
