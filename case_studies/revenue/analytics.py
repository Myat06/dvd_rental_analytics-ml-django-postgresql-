import os
import pandas as pd
from datetime import timedelta
from django.conf import settings

def _get_dataframe() -> pd.DataFrame:
    csv_path = os.path.join(settings.BASE_DIR, 'raw_data', 'revenue_clean.csv')
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df

def _filter_by_days(df: pd.DataFrame, days: int) -> pd.DataFrame:
    if df.empty:
        return df
    max_date = df['date'].max()
    cutoff_date = max_date - timedelta(days=days - 1)
    return df[df['date'] >= cutoff_date]

def get_revenue_kpis(days=120):
    df = _get_dataframe()
    if df.empty:
        return {
            "total_revenue": 0.0,
            "transaction_count": 0,
            "avg_transaction": 0.0,
            "data_source": "csv_unavailable"
        }
    
    df_filtered = _filter_by_days(df, days)
    total_amount = float(df_filtered['amount'].sum()) if not df_filtered.empty else 0.0
    tx_count = len(df_filtered)
    avg_tx = total_amount / tx_count if tx_count > 0 else 0.0

    return {
        "total_revenue": total_amount,
        "transaction_count": tx_count,
        "avg_transaction": avg_tx,
        "data_source": "csv_file"
    }

def get_revenue_trend(days=120):
    df = _get_dataframe()
    if df.empty:
        return []
        
    df_filtered = _filter_by_days(df, days)
    if df_filtered.empty:
        return []
        
    trend = df_filtered.groupby('date')['amount'].sum().reset_index()
    trend = trend.sort_values('date')
    return [
        {"date": str(row['date']), "amount": float(row['amount'])} 
        for _, row in trend.iterrows()
    ]

def get_revenue_by_category(days=120):
    df = _get_dataframe()
    if df.empty or 'film_category' not in df.columns:
        return []
        
    df_filtered = _filter_by_days(df, days)
    if df_filtered.empty:
        return []
        
    category_agg = df_filtered.groupby('film_category')['amount'].sum().reset_index()
    category_agg = category_agg.sort_values('amount', ascending=False)
    
    # Get top 5 best film categories
    top_5 = category_agg.head(5)
    
    return [
        {"category": str(row['film_category']), "amount": float(row['amount'])} 
        for _, row in top_5.iterrows()
    ]

def get_revenue_by_weekday(days=120):
    df = _get_dataframe()
    if df.empty:
        return []
        
    df_filtered = _filter_by_days(df, days)
    if df_filtered.empty:
        return []
        
    df_filtered = df_filtered.copy()
    df_filtered['date'] = pd.to_datetime(df_filtered['date'])
    df_filtered['weekday'] = df_filtered['date'].dt.day_name()
    
    weekday_agg = df_filtered.groupby('weekday')['amount'].sum().reset_index()
    
    sorter = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_agg['weekday'] = pd.Categorical(weekday_agg['weekday'], categories=sorter, ordered=True)
    weekday_agg = weekday_agg.sort_values('weekday')
    
    return [
        {"day": str(row['weekday']), "amount": float(row['amount'])} 
        for _, row in weekday_agg.iterrows()
    ]

def get_daily_totals_all():
    """
    Full daily revenue series for ML training.
    """
    df = _get_dataframe()
    if df.empty:
        return []
        
    trend = df.groupby('date')['amount'].sum().reset_index()
    trend = trend.sort_values('date')
    return [
        (row['date'], float(row['amount'])) 
        for _, row in trend.iterrows()
    ]
