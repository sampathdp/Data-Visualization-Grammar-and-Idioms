

import streamlit as st

try:
    from services.semantic_metrics import calculate_kpis
except ImportError:
    from steam_dashboard.services.semantic_metrics import calculate_kpis

def render_kpi_row_compact(df_filtered):
    """
    Renders 4 high-contrast KPI cards with explicit dark text and clear badge colors.
    """
    kpis = calculate_kpis(df_filtered)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1.5px solid #CBD5E1; border-left: 5px solid #2563EB; border-radius: 6px; padding: 10px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            <div style="font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">📦 Catalog Titles (N)</div>
            <div style="font-size: 1.45rem; font-weight: 800; color: #0F172A; margin-top: 2px;">{kpis['total_games']:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1.5px solid #CBD5E1; border-left: 5px solid #059669; border-radius: 6px; padding: 10px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            <div style="font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">💲 Median Retail Price</div>
            <div style="font-size: 1.45rem; font-weight: 800; color: #059669; margin-top: 2px;">${kpis['median_price']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1.5px solid #CBD5E1; border-left: 5px solid #D97706; border-radius: 6px; padding: 10px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            <div style="font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">⭐ Review Positivity</div>
            <div style="font-size: 1.45rem; font-weight: 800; color: #D97706; margin-top: 2px;">{kpis['median_positivity']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1.5px solid #CBD5E1; border-left: 5px solid #7C3AED; border-radius: 6px; padding: 10px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            <div style="font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">💬 Total Review Evidence</div>
            <div style="font-size: 1.45rem; font-weight: 800; color: #1E293B; margin-top: 2px;">{kpis['total_reviews']:,}</div>
        </div>
        """, unsafe_allow_html=True)
