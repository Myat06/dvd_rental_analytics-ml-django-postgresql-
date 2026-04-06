import pandas as pd
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from pathlib import Path

CSV_PATH = Path(settings.BASE_DIR) / 'raw_data' / 'customer_churn_features.csv'

class Command(BaseCommand):
    help = 'Extract from PostgreSQL → Transform → Save to CSV'

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting DB → CSV ETL...")
        
        # ── EXTRACT ──────────────────────────────────────────
        query = """
            SELECT
                c.customer_id,
                c.store_id,
                c.active,
                COUNT(r.rental_id)                          AS total_rentals,
                COALESCE(SUM(p.amount), 0)                  AS total_payment,
                COALESCE(AVG(
                    EXTRACT(EPOCH FROM (r.return_date - r.rental_date))/86400
                ), 0)                                       AS avg_rental_duration,
                MAX(r.rental_date)::DATE                    AS last_rental_date
            FROM customer c
            LEFT JOIN rental r  ON c.customer_id = r.customer_id
            LEFT JOIN payment p ON c.customer_id = p.customer_id
            GROUP BY c.customer_id, c.store_id, c.active
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            df = pd.DataFrame(cursor.fetchall(), columns=[d[0] for d in cursor.description])

        self.stdout.write(f"📥 Extracted {len(df)} customers")

        # ── TRANSFORM ─────────────────────────────────────────
        df['last_rental_date'] = pd.to_datetime(df['last_rental_date'])
        max_date = df['last_rental_date'].max()
        df['days_since_last_rental'] = (max_date - df['last_rental_date']).dt.days
        
        # Churn label (0/1)
        df['is_churn'] = (df['days_since_last_rental'] > 90).astype(int)
        df['last_rental_date'] = df['last_rental_date'].dt.strftime('%Y-%m-%d')
        
        self.stdout.write(f"🏷️  Churn distribution: {df['is_churn'].value_counts().to_dict()}")

        # ── LOAD TO CSV ───────────────────────────────────────
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(CSV_PATH, index=False)
        self.stdout.write(self.style.SUCCESS(f"✅ Saved to {CSV_PATH}"))