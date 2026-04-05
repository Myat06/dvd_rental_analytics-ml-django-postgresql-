import logging
from django.db import transaction
import pandas as pd
from case_studies.revenue.models import RevenueTransaction

logger = logging.getLogger(__name__)

def load_revenue_data(df: pd.DataFrame) -> int:
    """
    Bulk load transformed DataFrame into PostgreSQL.
    Uses ignore_conflicts=True for idempotent runs (safe for retries).
    """
    logger.info("📤 Loading data into PostgreSQL...")
    
    if df.empty:
        logger.warning("⚠️ No records to load")
        return 0

    records = [
        RevenueTransaction(
            transaction_id=str(row['transaction_id']),
            date=row['date'],
            transaction_type=row['type'],
            amount=row['amount'],
            film_id=row.get('film_id'),
            customer_id=row.get('customer_id'),
            store_id=row.get('store_id')
        )
        for _, row in df.iterrows()
    ]

    # Bulk insert in batches for memory efficiency
    RevenueTransaction.objects.bulk_create(
        records,
        ignore_conflicts=True,  # Skips duplicates safely
        batch_size=1000
    )
    
    logger.info(f"✅ Successfully loaded {len(records)} records")
    return len(records)