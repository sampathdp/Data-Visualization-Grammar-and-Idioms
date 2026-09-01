
import os
import re
import numpy as np
import pandas as pd
import streamlit as st

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'steam-games.csv')
LOCAL_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'steam.csv')

def parse_price(val) -> float:
    """
    Robustly parses raw price strings, handling currency symbols, 'Free', and INR/USD conversions.
    """
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip().lower()
    if 'free' in val_str:
        return 0.0
    cleaned = re.sub(r'[^\d.]', '', val_str)
    if not cleaned:
        return np.nan
    try:
        p = float(cleaned)
        # Convert INR amounts (> 100) to approximate USD ($1 ~= 83 INR)
        return round(p / 83.0, 2) if p > 100 else round(p, 2)
    except Exception:
        return np.nan

def get_primary_genre(genre_str) -> str:
    """
    Extracts the most relevant primary genre from comma-separated genre string.
    """
    if pd.isna(genre_str):
        return 'Other'
    genres = [g.strip() for g in str(genre_str).split(',') if g.strip()]
    priority = ['Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 'Casual', 'Indie', 'Sports', 'Racing', 'Massively Multiplayer']
    for p in priority:
        if p in genres:
            return p
    return genres[0] if genres else 'Other'

@st.cache_data(show_spinner=True)
def load_raw_data() -> pd.DataFrame:
    """
    Loads raw CSV and performs initial cleaning and type parsing with caching.
    """
    path_to_use = DATA_PATH if os.path.exists(DATA_PATH) else LOCAL_DATA_PATH
    if not os.path.exists(path_to_use):
        # Fallback to direct current working directory
        path_to_use = 'steam-games.csv'

    df = pd.read_csv(path_to_use)
    
    # 1. Parse Prices
    df['price_usd'] = df['discounted_price'].apply(parse_price).fillna(df['original_price'].apply(parse_price))
    
    # 2. Parse Dates and Years
    df['release_datetime'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_datetime'].dt.year
    
    # 3. Clean categorical strings
    df['developer'] = df['developer'].fillna('Unknown Developer').astype(str).str.strip()
    df['publisher'] = df['publisher'].fillna('Self-Published / Unknown').astype(str).str.strip()
    
    # 4. Genre lists and Primary Genre
    df['genres'] = df['genres'].fillna('Uncategorized').astype(str)
    df['genres_list'] = df['genres'].apply(lambda s: [g.strip() for g in s.split(',') if g.strip()])
    df['primary_genre'] = df['genres'].apply(get_primary_genre)
    
    # 5. Review metrics
    df['overall_review_%'] = pd.to_numeric(df['overall_review_%'], errors='coerce')
    df['overall_review_count'] = pd.to_numeric(df['overall_review_count'], errors='coerce').fillna(0).astype(int)
    
    # 6. Platforms
    df['win_support'] = df['win_support'].fillna(False).astype(bool)
    df['mac_support'] = df['mac_support'].fillna(False).astype(bool)
    df['linux_support'] = df['linux_support'].fillna(False).astype(bool)
    
    # Platform summary label
    def get_platform_label(row):
        platforms = []
        if row['win_support']: platforms.append('Win')
        if row['mac_support']: platforms.append('Mac')
        if row['linux_support']: platforms.append('Linux')
        return '+'.join(platforms) if platforms else 'None'
    
    df['platform_bundle'] = df.apply(get_platform_label, axis=1)

    # 7. Price band
    def get_price_band(price):
        if pd.isna(price): return 'Unknown'
        if price == 0: return 'Free'
        if price < 5.0: return 'Under $5'
        if price < 15.0: return '$5 – $14.99'
        if price < 30.0: return '$15 – $29.99'
        if price < 60.0: return '$30 – $59.99'
        return '$60+'
    
    df['price_band'] = df['price_usd'].apply(get_price_band)
    
    return df

@st.cache_data
def get_exploded_genre_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns an exploded dataframe where each (app_id, genre) pair is an individual row.
    Guarantees that games with multiple genres are counted accurately without string containment errors.
    """
    df_exp = df.explode('genres_list').rename(columns={'genres_list': 'genre'})
    df_exp['genre'] = df_exp['genre'].fillna('Uncategorized')
    return df_exp

@st.cache_data
def get_unique_genres(df: pd.DataFrame) -> list:
    """
    Returns sorted list of top valid genres present in dataset.
    """
    exploded = df['genres_list'].explode().dropna()
    top_genres = exploded.value_counts()
    return top_genres[top_genres >= 10].index.tolist()
