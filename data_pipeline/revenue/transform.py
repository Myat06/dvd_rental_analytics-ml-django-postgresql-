import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Mapping raw system types to Django model choices
TYPE_MAP = {
    'rent': 'rental', 'late': 'late_fee', 'refund': 'refund', 
    'discount': 'discount', 'rental': 'rental', 'late_fee': 'late_fee'
}

def transform_revenue_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean, validate, and standardize revenue data.
    Returns a DataFrame ready for bulk loading.
    """
    logger.info("🔄 Transforming revenue data...")
    df = df.copy()

    # 1. Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # 2. Validate required columns
    required_cols = ['transaction_id', 'date', 'type', 'amount']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"❌ Missing required columns: {missing}")

    # 3. Clean & parse dates
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
    df = df.dropna(subset=['date'])

    # 4. Clean amounts (remove negatives, non-numeric)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df[df['amount'] > 0]

    # 5. Map transaction types safely
    df['type'] = df['type'].str.strip().str.lower().map(TYPE_MAP).fillna('rental')

    # 6. Handle optional dimension keys
    for col in ['film_id', 'customer_id', 'store_id', 'film_category']:
        if col not in df.columns:
            df[col] = None
        elif col != 'film_category':
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')  # Nullable int

    # 7. Deduplicate by transaction_id (idempotent loading)
    df = df.drop_duplicates(subset=['transaction_id'], keep='first')

    logger.info(f"✅ Transformed data ready: {len(df)} valid rows")
    return df[required_cols + ['film_id', 'customer_id', 'store_id', 'film_category']]