import logging

import pandas as pd
import psycopg2
from django.conf import settings

logger = logging.getLogger(__name__)

def extract_revenue_data(source_path: str = None) -> pd.DataFrame:
    """
    Extract revenue data DIRECTLY from PostgreSQL payment table.
    
    Args:
        source_path: Ignored (kept for API compatibility with existing pipeline)
    
    Returns:
        DataFrame with columns: transaction_id, date, type, amount, film_id, customer_id, store_id
    """
    logger.info("📥 Extracting revenue data from PostgreSQL payment table...")
    
    # Get DB credentials from Django settings
    db_config = settings.DATABASES['default']
    
    # Build connection string for psycopg2/pandas
    conn_params = {
        'dbname': db_config['NAME'],
        'user': db_config['USER'],
        'password': db_config['PASSWORD'],
        'host': db_config.get('HOST', 'localhost'),
        'port': db_config.get('PORT', '5432'),
    }
    
    # Query the payment table + join to get film context
    query = """
        SELECT 
            p.payment_id::text as transaction_id,
            p.payment_date::date as date,
            'rental' as type,  -- Sample DB only has rental payments
            p.amount,
            i.film_id,
            p.customer_id,
            s.store_id,
            c.name as film_category
        FROM payment p
        JOIN rental r ON p.rental_id = r.rental_id
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN store s ON i.store_id = s.store_id
        LEFT JOIN film_category fc ON i.film_id = fc.film_id
        LEFT JOIN category c ON fc.category_id = c.category_id
        ORDER BY p.payment_date
    """
    
    try:
        with psycopg2.connect(**conn_params) as conn:
            df = pd.read_sql_query(query, conn)

        logger.info(f"✅ Extracted {len(df):,} payment records from PostgreSQL")
        logger.info(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
        logger.info(f"💰 Total revenue: ${df['amount'].sum():,.2f}")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Failed to extract data: {str(e)}")
        raise