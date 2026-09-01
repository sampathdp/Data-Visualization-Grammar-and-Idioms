import numpy as np
import pandas as pd

def calculate_review_positivity(positive_reviews: pd.Series, negative_reviews: pd.Series) -> pd.Series:
    """
    Computes Review Positivity %: (Positive / (Positive + Negative)) * 100.
    Handles division by zero by returning NaN.
    """
    total = positive_reviews + negative_reviews
    return np.where(total > 0, (positive_reviews / total) * 100.0, np.nan)

def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculates context-sensitive KPIs for the currently filtered dataset.
    Returns standard summary metrics with exact sample sizes.
    """
    if df.empty:
        return {
            'total_games': 0,
            'median_price': 0.0,
            'mean_price': 0.0,
            'median_positivity': 0.0,
            'total_reviews': 0,
            'median_reviews': 0.0,
            'multiplatform_share': 0.0,
            'free_to_play_count': 0
        }

    total_games = int(df['app_id'].nunique())
    median_price = float(df['price_usd'].median()) if 'price_usd' in df.columns and not df['price_usd'].isna().all() else 0.0
    mean_price = float(df['price_usd'].mean()) if 'price_usd' in df.columns and not df['price_usd'].isna().all() else 0.0
    
    positivity_series = df['overall_review_%'].dropna()
    median_positivity = float(positivity_series.median()) if not positivity_series.empty else 0.0
    
    review_counts = df['overall_review_count'].dropna()
    total_reviews = int(review_counts.sum()) if not review_counts.empty else 0
    median_reviews = float(review_counts.median()) if not review_counts.empty else 0.0
    
    # Multiplatform definition: supported on 2 or more OS platforms
    if all(col in df.columns for col in ['win_support', 'mac_support', 'linux_support']):
        platform_count = df['win_support'].astype(int) + df['mac_support'].astype(int) + df['linux_support'].astype(int)
        multiplatform_share = float((platform_count >= 2).mean() * 100.0)
    else:
        multiplatform_share = 0.0

    free_count = int((df['price_usd'] == 0.0).sum()) if 'price_usd' in df.columns else 0

    return {
        'total_games': total_games,
        'median_price': median_price,
        'mean_price': mean_price,
        'median_positivity': median_positivity,
        'total_reviews': total_reviews,
        'median_reviews': median_reviews,
        'multiplatform_share': multiplatform_share,
        'free_to_play_count': free_count
    }

def calculate_saturation_index(df_full: pd.DataFrame, genre: str, year_window: tuple = (2018, 2024)) -> dict:
    """
    Computes genre competitive saturation index relative to overall market growth.
    """
    df_window = df_full[(df_full['release_year'] >= year_window[0]) & (df_full['release_year'] <= year_window[1])]
    if df_window.empty:
        return {'saturation_index': 0.0, 'genre_share_%': 0.0, 'total_genre_titles': 0}
    
    total_market_titles = df_window['app_id'].nunique()
    genre_titles = df_window[df_window['genres_list'].apply(lambda x: genre in x if isinstance(x, list) else False)]['app_id'].nunique()
    
    genre_share = (genre_titles / total_market_titles * 100.0) if total_market_titles > 0 else 0.0
    
    return {
        'total_market_titles': total_market_titles,
        'total_genre_titles': genre_titles,
        'genre_share_%': round(genre_share, 2),
        'saturation_rating': 'High Density' if genre_share > 25 else ('Moderate Density' if genre_share > 10 else 'Niche / Specialized')
    }

def run_what_if_benchmark(
    df: pd.DataFrame,
    genre: str,
    target_price: float,
    platforms: list,
    year_range: tuple = (2019, 2024),
    min_reviews: int = 20
) -> dict:
    """
    Evaluates a hypothetical game configuration against historical cohorts.
    Returns empirical benchmarks and positioning metrics.
    """
    # 1. Filter by temporal window and minimum evidence
    cohort = df[
        (df['release_year'] >= year_range[0]) & 
        (df['release_year'] <= year_range[1]) &
        (df['overall_review_count'] >= min_reviews)
    ].copy()
    
    # 2. Filter by genre
    if 'genres_list' in cohort.columns:
        cohort = cohort[cohort['genres_list'].apply(lambda gl: genre in gl if isinstance(gl, list) else False)]
    elif 'primary_genre' in cohort.columns:
        cohort = cohort[cohort['primary_genre'] == genre]

    # 3. Filter by platform compatibility
    for p in platforms:
        if p.lower() == 'windows' and 'win_support' in cohort.columns:
            cohort = cohort[cohort['win_support'] == True]
        elif p.lower() == 'mac' and 'mac_support' in cohort.columns:
            cohort = cohort[cohort['mac_support'] == True]
        elif p.lower() == 'linux' and 'linux_support' in cohort.columns:
            cohort = cohort[cohort['linux_support'] == True]

    sample_size = len(cohort)
    if sample_size == 0:
        return {
            'sample_size': 0,
            'status': 'Insufficient historical comparables'
        }

    cohort_prices = cohort['price_usd'].dropna()
    price_percentile = float((cohort_prices <= target_price).mean() * 100.0) if not cohort_prices.empty else 50.0

    return {
        'sample_size': sample_size,
        'status': 'Valid Cohort',
        'median_price': float(cohort['price_usd'].median()),
        'median_positivity': float(cohort['overall_review_%'].median()),
        'mean_positivity': float(cohort['overall_review_%'].mean()),
        'median_reviews': float(cohort['overall_review_count'].median()),
        'p75_reviews': float(cohort['overall_review_count'].quantile(0.75)),
        'price_percentile': round(price_percentile, 1),
        'free_share_%': round(float((cohort['price_usd'] == 0).mean() * 100.0), 1),
        'top_publishers': cohort['publisher'].value_counts().head(5).to_dict(),
        'top_developers': cohort['developer'].value_counts().head(5).to_dict()
    }
