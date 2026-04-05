"""
Single entry point for the revenue ETL pipeline (coursework-facing module).
"""

import logging
from typing import Optional, Tuple

import os
from django.conf import settings

from .extract import extract_revenue_data
from .transform import transform_revenue_data
from .load import load_revenue_data
from .olap import refresh_revenue_daily_olap

logger = logging.getLogger(__name__)


def run_revenue_etl(source_path: Optional[str] = None) -> Tuple[int, int, str]:
    """
    Extract → Transform → Save to CSV → Load → refresh OLAP aggregates.

    Returns:
        (loaded_transaction_count, olap_row_count, csv_path)
    """
    logger.info("Starting revenue ETL pipeline")
    df_raw = extract_revenue_data(source_path)
    df_clean = transform_revenue_data(df_raw)
    
    # Save the dataframe as CSV to the raw_data directory
    csv_path = os.path.join(settings.BASE_DIR, 'raw_data', 'revenue_clean.csv')
    df_clean.to_csv(csv_path, index=False)
    logger.info(f"Saved transformed DataFrame to CSV at {csv_path}")

    loaded = load_revenue_data(df_clean)
    olap_rows = refresh_revenue_daily_olap()
    return loaded, olap_rows, csv_path
