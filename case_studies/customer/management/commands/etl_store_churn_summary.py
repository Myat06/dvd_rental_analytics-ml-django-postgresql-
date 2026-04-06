import os
import pandas as pd
import joblib
from django.core.management.base import BaseCommand
from django.conf import settings
from case_studies.customer.models import StoreChurnSummary

CSV_PATH = os.path.join(settings.BASE_DIR, 'raw_data', 'customer_churn_features.csv')
MODEL_PATH = os.path.join(settings.BASE_DIR, 'case_studies', 'customer', 'ml_models', 'churn_model.pkl')

class Command(BaseCommand):
    help = 'ETL: Load CSV + Model → Compute store churn summary → Save to DB'

    def handle(self, *args, **kwargs):
        self.stdout.write("🏪 Starting Store Churn Summary ETL (CSV + ML)...")
        
        if not os.path.exists(CSV_PATH):
            self.stdout.write(self.style.ERROR(f"❌ Missing {CSV_PATH}. Run `python manage.py etl_customer_churn` first."))
            return
            
        if not os.path.exists(MODEL_PATH):
            self.stdout.write(self.style.WARNING(f"⚠️  Missing model {MODEL_PATH}. Run `python manage.py train_churn_model` first."))
            return
        
        # Load data + predict
        df = pd.read_csv(CSV_PATH)
        model = joblib.load(MODEL_PATH)
        features = ['store_id', 'active', 'total_rentals', 'total_payment', 'avg_rental_duration']
        df['predicted_churn'] = model.predict(df[features])
        
        # Aggregate store summary
        summary = df.groupby('store_id').agg(
            total_customers=('customer_id', 'count'),
            churned_customers=('predicted_churn', 'sum'),
            total_revenue=('total_payment', 'sum')
        ).reset_index()
        
        summary['churn_rate'] = (summary['churned_customers'] / summary['total_customers'] * 100).round(2)
        
        # Save to DB
        StoreChurnSummary.objects.all().delete()
        records = [
            StoreChurnSummary(
                store_id=int(row['store_id']),
                total_customers=int(row['total_customers']),
                churned_customers=int(row['churned_customers']),
                churn_rate=float(row['churn_rate']),
                total_revenue=float(row['total_revenue'])
            ) for _, row in summary.iterrows()
        ]
        StoreChurnSummary.objects.bulk_create(records)
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Loaded {len(records)} store summaries to DB!")
        )
