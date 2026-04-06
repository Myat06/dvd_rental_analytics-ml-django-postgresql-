import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

# 🔧 Aligned with raw_data/ convention
CSV_PATH = os.path.join(settings.BASE_DIR, 'raw_data', 'customer_rfm.csv')

class Command(BaseCommand):
    help = 'ETL: Calculate RFM scores per customer & save to CSV'

    def handle(self, *args, **kwargs):
        self.stdout.write("📊 Starting RFM ETL...")
        
        query = """
            SELECT c.customer_id, c.store_id,
                   MAX(r.rental_date)::DATE AS last_rental_date,
                   COUNT(r.rental_id) AS frequency,
                   COALESCE(SUM(p.amount), 0) AS monetary
            FROM customer c
            LEFT JOIN rental r ON c.customer_id = r.customer_id
            LEFT JOIN payment p ON c.customer_id = p.customer_id
            GROUP BY c.customer_id, c.store_id
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            df = pd.DataFrame(cursor.fetchall(), columns=[d[0] for d in cursor.description])

        self.stdout.write(f"📥 Extracted {len(df)} customers")

        # ── TRANSFORM ─────────────────────────────────────────
        max_date = pd.to_datetime(df['last_rental_date']).max()
        df['recency'] = (max_date - pd.to_datetime(df['last_rental_date'])).dt.days
        
        # Quantile scoring (1-3) - handles ties safely
        df['r_score'] = pd.qcut(df['recency'].rank(method='first'), q=3, labels=[3,2,1]).astype(int)
        df['f_score'] = pd.qcut(df['frequency'].rank(method='first'), q=3, labels=[1,2,3]).astype(int)
        df['m_score'] = pd.qcut(df['monetary'].rank(method='first'), q=3, labels=[1,2,3]).astype(int)
        df['rfm_score'] = df['r_score'] + df['f_score'] + df['m_score']

        # ── SAVE ──────────────────────────────────────────────
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        df.to_csv(CSV_PATH, index=False)
        self.stdout.write(self.style.SUCCESS(f"✅ RFM saved to {CSV_PATH}"))