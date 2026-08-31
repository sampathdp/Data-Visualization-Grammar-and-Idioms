"""
Explanatory Storytelling Visual Components for Steam Market Intelligence.
Features:
1. Annotated Timeline (Supply Surge & Deregulation)
2. Advanced Market Share Treemap (Hierarchical Space-Filling Idiom)
3. The Small-Sample Rating Illusion (Log-Scale Evidence Plot)
4. Geospatial Global Studio Hubs Map (Spatial / Choropleth Idiom)
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

TEXT_COLOR = "#0F172A"
AXIS_COLOR = "#334155"
GRID_COLOR = "#E2E8F0"

COUNTRY_LOOKUP = {
    'USA': ['Valve', 'Electronic Arts', 'Devolver Digital', '2K', 'Bethesda Softworks', 'Choice of Games', 'Big Fish Games', 'Sekai Project', 'Kagura Games', 'Winged Cloud'],
    'JPN': ['Square Enix', 'SEGA', 'CAPCOM Co., Ltd.', 'BANDAI NAMCO Entertainment', 'KOEI TECMO GAMES CO., LTD.', 'Kairosoft Co.,Ltd'],
    'FRA': ['Ubisoft', 'Focus Entertainment', 'Plug In Digital', 'Microids', 'RewindApp', 'Dontnod Entertainment'],
    'GBR': ['Slitherine Ltd.', 'Team17', 'Rebellion', 'Codemasters', 'Sumo Digital', 'Ripknot Systems'],
    'DEU': ['EpiXR Games UG', 'Daedalic Entertainment', 'Crytek', 'Assemble Entertainment', 'Deck13'],
    'POL': ['CD PROJEKT RED', '11 bit studios', 'Techland', 'PlayWay S.A.', 'Fulqrum Publishing'],
    'SWE': ['Paradox Interactive', 'Coffee Stain Publishing', 'Fatshark', 'Arrowhead Game Studios'],
    'NLD': ['Sokpop Collective', 'Guerrilla', 'Triumph Studios'],
    'RUS': ['Alawar Casual', 'Laush Studio', 'Laush Dmitriy Sergeevich', 'Dnovel', 'Elephant Games', 'Blender Games'],
    'CAN': ['Strategy First', 'BioWare', 'Klei Entertainment', 'Behaviour Interactive'],
    'AUS': ['Team Cherry', 'League of Geeks', 'Blowfish Studios'],
    'FIN': ['Tero Lunkka', 'Remedy Entertainment', 'Housemarque'],
    'ITA': ['505 Games', 'Milestone S.r.l.', 'Kunos Simulazioni'],
    'ESP': ['MercurySteam', 'Tequila Works', 'Novarama'],
    'KOR': ['KRAFTON, Inc.', 'NEXON', 'Pearl Abyss', 'Smilegate'],
    'CHN': ['NetEase Games', 'Tencent Games', 'Gamera Games', 'bilibili']
}

def render_story_stage_1(df: pd.DataFrame):
    """
    Stage 1: 'Steam Became Increasingly Crowded'
    Annotated timeline showing catalogue deregulation points (Greenlight 2012, Steam Direct 2017).
    Dynamically adapts to the active filtered year range and data bounds.
    """
    if df.empty or 'release_year' not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            height=250,
            annotations=[dict(text="No data matching active filters", showarrow=False, font=dict(size=12, color=TEXT_COLOR))]
        )
        return fig

    agg = df.groupby('release_year')['app_id'].nunique().reset_index()
    agg = agg.dropna().sort_values('release_year')

    if agg.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            height=250,
            annotations=[dict(text="No data matching active filters", showarrow=False, font=dict(size=12, color=TEXT_COLOR))]
        )
        return fig

    min_yr = int(agg['release_year'].min())
    max_yr = int(agg['release_year'].max())

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=agg['release_year'],
        y=agg['app_id'],
        mode='lines+markers',
        fill='tozeroy',
        fillcolor='rgba(78, 121, 167, 0.15)',
        line=dict(color='#4E79A7', width=2.5),
        marker=dict(size=6, color='#4E79A7'),
        name='Annual Releases',
        hovertemplate='Year %{x}: <b>%{y:,} releases</b><extra></extra>'
    ))

    # Add Deregulation Annotations ONLY if the milestone year falls within the active filtered range
    has_custom_annotation = False
    if min_yr <= 2012 <= max_yr and 2012 in agg['release_year'].values:
        val_2012 = float(agg[agg['release_year'] == 2012]['app_id'].values[0])
        fig.add_vline(x=2012, line_dash="dot", line_color="#D97706", line_width=1.5)
        fig.add_annotation(
            x=2012, y=val_2012,
            text="<b>2012: Greenlight</b><br>Community voting access",
            showarrow=True, arrowhead=2, arrowcolor="#D97706", ax=-45, ay=-35,
            bgcolor="#FFFFFF", bordercolor="#D97706", borderwidth=1,
            font=dict(size=8.5, color=TEXT_COLOR)
        )
        has_custom_annotation = True

    if min_yr <= 2017 <= max_yr and 2017 in agg['release_year'].values:
        val_2017 = float(agg[agg['release_year'] == 2017]['app_id'].values[0])
        fig.add_vline(x=2017, line_dash="dot", line_color="#E15759", line_width=1.5)
        fig.add_annotation(
            x=2017, y=val_2017,
            text="<b>2017: Steam Direct</b><br>Direct fee submission surge",
            showarrow=True, arrowhead=2, arrowcolor="#E15759", ax=-55, ay=-35,
            bgcolor="#FFFFFF", bordercolor="#E15759", borderwidth=1,
            font=dict(size=8.5, color=TEXT_COLOR)
        )
        has_custom_annotation = True

    # If neither 2012 nor 2017 is in the active year window, highlight the peak year in the selected window
    if not has_custom_annotation and len(agg) > 1:
        peak_row = agg.loc[agg['app_id'].idxmax()]
        fig.add_annotation(
            x=peak_row['release_year'], y=peak_row['app_id'],
            text=f"<b>Peak ({int(peak_row['release_year'])})</b>: {int(peak_row['app_id']):,} releases",
            showarrow=True, arrowhead=2, arrowcolor="#4E79A7", ax=0, ay=-35,
            bgcolor="#FFFFFF", bordercolor="#4E79A7", borderwidth=1,
            font=dict(size=8.5, color=TEXT_COLOR)
        )

    # Tight x-axis to exactly match the active data bounds (prevents ghost gaps to 2010)
    fig.update_layout(
        font=dict(family="Segoe UI, Arial, sans-serif", size=10, color=TEXT_COLOR),
        template="plotly_white",
        height=250,
        margin=dict(l=40, r=10, t=15, b=20),
        xaxis=dict(
            range=[min_yr - 0.25, max_yr + 0.25],
            dtick=2 if (max_yr - min_yr) > 6 else 1,
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            gridcolor=GRID_COLOR,
            tickfont=dict(size=9, color=TEXT_COLOR)
        ),
        yaxis=dict(
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            gridcolor=GRID_COLOR,
            tickfont=dict(size=9, color=TEXT_COLOR),
            title=None
        ),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        showlegend=False
    )
    return fig


def render_story_stage_2_treemap(df_exploded: pd.DataFrame):
    """
    Stage 2: Advanced Treemap Idiom (Hierarchical Space-Filling Representation).
    Area = Title Volume (N), Color = Median Review Positivity %.
    """
    if df_exploded.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            height=250,
            annotations=[dict(text="No data matching active filters", showarrow=False, font=dict(size=12, color=TEXT_COLOR))]
        )
        return fig

    df_chart = df_exploded.copy()
    
    agg = df_chart.groupby('genre').agg(
        titles=('app_id', 'nunique'),
        median_positivity=('overall_review_%', 'median'),
        median_price=('price_usd', 'median')
    ).reset_index()

    min_count = 5 if len(agg) > 10 else 1
    agg = agg[agg['titles'] >= min_count].sort_values('titles', ascending=False)
    if agg.empty:
        agg = df_chart.groupby('genre').agg(
            titles=('app_id', 'nunique'),
            median_positivity=('overall_review_%', 'median'),
            median_price=('price_usd', 'median')
        ).reset_index().sort_values('titles', ascending=False)

    fig = px.treemap(
        agg,
        path=['genre'],
        values='titles',
        color='median_positivity',
        color_continuous_scale='Blues',
        range_color=[60, 90],
        template="plotly_white",
        height=250,
        hover_data={'titles': ':,', 'median_positivity': ':.1f', 'median_price': ':.2f'},
        labels={'titles': 'Catalog Titles', 'median_positivity': 'Positivity (%)', 'genre': 'Genre'}
    )

    fig.update_traces(
        textinfo="label+value+percent entry",
        textfont=dict(size=11, color="#FFFFFF", family="Segoe UI, Arial"),
        marker=dict(pad=dict(t=2, l=2, r=2, b=2))
    )

    fig.update_layout(
        font=dict(family="Segoe UI, Arial, sans-serif", size=10, color=TEXT_COLOR),
        margin=dict(l=5, r=5, t=10, b=10),
        coloraxis_colorbar=dict(
            title=dict(text="Pos %", font=dict(size=9, color=TEXT_COLOR)),
            thickness=10,
            tickfont=dict(size=8, color=TEXT_COLOR)
        ),
        paper_bgcolor='#FFFFFF'
    )
    return fig


def render_story_stage_4(df: pd.DataFrame):
    """
    Stage 3: 'The Small-Sample Illusion'
    Demonstrates statistical uncertainty when evaluating ratings with low evidence vs high evidence.
    """
    sample = df.dropna(subset=['overall_review_%', 'overall_review_count']).copy()
    if sample.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            height=250,
            annotations=[dict(text="No data matching active filters", showarrow=False, font=dict(size=12, color=TEXT_COLOR))]
        )
        return fig

    # Compute dynamic thresholds based on current filtered dataset
    min_count_in_data = sample['overall_review_count'].min()
    max_count_in_data = sample['overall_review_count'].max()
    
    low_cutoff = max(min_count_in_data + 10, int(sample['overall_review_count'].quantile(0.20)))
    high_cutoff = max(low_cutoff + 50, int(sample['overall_review_count'].quantile(0.70)))

    low_evidence = sample[sample['overall_review_count'] <= low_cutoff].head(100)
    high_evidence = sample[sample['overall_review_count'] >= high_cutoff].head(200)

    if low_evidence.empty and high_evidence.empty:
        demo_df = sample.head(300).copy()
        demo_df['Cohort Type'] = 'Filtered Commercial Titles'
        label_low = 'Low Evidence'
        label_high = 'High Evidence'
    else:
        label_low = f'Niche / Low Evidence (N ≤ {low_cutoff})'
        label_high = f'Validated Commercial (N ≥ {high_cutoff})'
        demo_df = pd.concat([low_evidence, high_evidence])
        demo_df['Cohort Type'] = np.where(
            demo_df['overall_review_count'] <= low_cutoff,
            label_low,
            label_high
        )

    color_map = {label_low: '#E15759', label_high: '#4E79A7', 'Filtered Commercial Titles': '#4E79A7'}

    fig = px.scatter(
        demo_df,
        x='overall_review_count',
        y='overall_review_%',
        color='Cohort Type',
        color_discrete_map=color_map,
        log_x=True,
        template="plotly_white",
        height=250,
        hover_name='title',
        labels={'overall_review_count': 'Evidence (Log Scale)', 'overall_review_%': 'Positivity (%)'}
    )

    # Point to the actual highest rating title with the lowest evidence in the dataset
    if not low_evidence.empty:
        top_low_cand = low_evidence.sort_values(by=['overall_review_%', 'overall_review_count'], ascending=[False, True]).iloc[0]
        actual_x = float(top_low_cand['overall_review_count'])
        actual_y = float(top_low_cand['overall_review_%'])
        fig.add_annotation(
            x=np.log10(max(actual_x, 1)), y=actual_y,
            text=f"<b>Low-Evidence ({int(actual_y)}%)</b><br>N = {int(actual_x)} reviews",
            showarrow=True, arrowhead=2, arrowcolor="#E15759", ax=50, ay=30,
            bgcolor="#FFFFFF", bordercolor="#E15759", borderwidth=1,
            font=dict(size=8.5, color=TEXT_COLOR)
        )

    fig.update_layout(
        font=dict(family="Segoe UI, Arial, sans-serif", size=10, color=TEXT_COLOR),
        margin=dict(l=35, r=10, t=10, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None, font=dict(size=8.5, color=TEXT_COLOR)),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, tickfont=dict(size=9, color=TEXT_COLOR)),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, range=[20, 105], tickfont=dict(size=9, color=TEXT_COLOR), title=None)
    )
    return fig


def render_story_stage_geospatial_map(df: pd.DataFrame):
    """
    Stage 4: Geospatial / Geographical Choropleth Map (Spatial Dimension).
    Maps global game publishing & studio production hubs by Country.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            height=250,
            annotations=[dict(text="No data matching active filters", showarrow=False, font=dict(size=12, color=TEXT_COLOR))]
        )
        return fig

    dev_map = {}
    for iso, names in COUNTRY_LOOKUP.items():
        for name in names:
            dev_map[name.lower()] = iso

    def map_country(row):
        dev = str(row['developer']).lower()
        pub = str(row['publisher']).lower()
        for name, iso in dev_map.items():
            if name in dev or name in pub:
                return iso
        if 'ltd' in dev or 'uk' in dev: return 'GBR'
        if 'inc' in dev or 'llc' in dev: return 'USA'
        if 'japan' in dev or 'tokyo' in dev: return 'JPN'
        if 'france' in dev: return 'FRA'
        if 'germany' in dev or 'gmbh' in dev: return 'DEU'
        if 'poland' in dev: return 'POL'
        if 'canada' in dev: return 'CAN'
        if 'russia' in dev or 'rus' in dev: return 'RUS'
        if 'sweden' in dev: return 'SWE'
        if 'australia' in dev: return 'AUS'
        return 'USA'

    df_map = df.copy()
    df_map['country_iso'] = df_map.apply(map_country, axis=1)

    country_agg = df_map.groupby('country_iso').agg(
        total_games=('app_id', 'nunique'),
        median_positivity=('overall_review_%', 'median'),
        total_reviews=('overall_review_count', 'sum')
    ).reset_index()

    # Log intensity for balanced global coloring
    country_agg['log_volume'] = np.log10(country_agg['total_games'].clip(lower=1))

    fig = px.choropleth(
        country_agg,
        locations="country_iso",
        color="log_volume",
        hover_name="country_iso",
        hover_data={
            'country_iso': False,
            'log_volume': False,
            'total_games': ':,',
            'median_positivity': ':.1f',
            'total_reviews': ':,'
        },
        color_continuous_scale="Blues",
        labels={'total_games': 'Catalog Titles (N)', 'median_positivity': 'Positivity (%)', 'total_reviews': 'Total Reviews'},
        template="plotly_white",
        height=250
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="#CBD5E1",
        showocean=True,
        oceancolor="#F8FAFC",
        showland=True,
        landcolor="#FFFFFF",
        projection_type="natural earth",
        resolution=110
    )

    fig.update_layout(
        font=dict(family="Segoe UI, Arial, sans-serif", size=10, color=TEXT_COLOR),
        margin=dict(l=0, r=0, t=5, b=5),
        coloraxis_showscale=False,
        paper_bgcolor='#FFFFFF',
        geo=dict(bgcolor='#FFFFFF')
    )
    return fig
