import os
import pandas as pd
import joblib
from django.core.management.base import BaseCommand
from django.conf import settings
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from case_studies.customer.models import ModelInfo

CSV_PATH = os.path.join(settings.BASE_DIR, 'raw_data', 'customer_churn_features.csv')
MODEL_DIR = os.path.join(settings.BASE_DIR, 'case_studies', 'customer', 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'churn_model.pkl')

class Command(BaseCommand):
    help = 'Train churn model directly from CSV'

    def handle(self, *args, **kwargs):
        self.stdout.write(f"📊 Loading data from {CSV_PATH}...")
        df = pd.read_csv(CSV_PATH)

        # Features (exclude days_since_last_rental to prevent data leakage)
        features = ['store_id', 'active', 'total_rentals', 'total_payment', 'avg_rental_duration']
        X, y = df[features], df['is_churn']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred)
        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(model, X, y, cv=5)

        self.stdout.write(f"\n📈 Accuracy: {accuracy:.2%} | CV Mean: {cv_scores.mean():.2%}")
        self.stdout.write(f"\n🔑 Feature Importance:\n{pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)}")
        self.stdout.write(f"\n📋 Report:\n{report}")

        # Save model
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        self.stdout.write(self.style.SUCCESS(f"💾 Model saved: {MODEL_PATH}"))

        # Log to DB
        ModelInfo.objects.create(
            model_name='RandomForestChurn_v1',
            model_file=MODEL_PATH,
            training_data=CSV_PATH,
            training_date=pd.Timestamp.now(),
            model_summary=report
        )
        self.stdout.write(self.style.SUCCESS("✅ Model metadata saved to DB!"))