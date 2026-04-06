import os
import pandas as pd
import joblib
from django.conf import settings

CSV_PATH = os.path.join(settings.BASE_DIR, 'raw_data', 'customer_churn_features.csv')
MODEL_PATH = os.path.join(settings.BASE_DIR, 'case_studies', 'customer', 'ml_models', 'churn_model.pkl')

def _load_data_and_model():
    """Load CSV + Model → Add prediction columns"""
    df = pd.read_csv(CSV_PATH)
    model = joblib.load(MODEL_PATH)
    features = ['store_id', 'active', 'total_rentals', 'total_payment', 'avg_rental_duration']
    df['churn_probability'] = model.predict_proba(df[features])[:, 1]
    df['predicted_churn'] = model.predict(df[features])
    return df

def get_dashboard_stats():
    """Aggregate stats directly from CSV for dashboard"""
    df = _load_data_and_model()
    total = len(df)
    churned = len(df[df['predicted_churn'] == 1])
    churn_rate = (churned / total) * 100 if total > 0 else 0

    store_summary = df.groupby('store_id').agg(
        total_customers=('customer_id', 'count'),
        churned_customers=('predicted_churn', 'sum'),
        total_revenue=('total_payment', 'sum'),
        avg_risk=('churn_probability', 'mean')
    ).reset_index()
    store_summary['churn_rate'] = (store_summary['churned_customers'] / store_summary['total_customers'] * 100).round(2)

    # Risk distribution (convert Interval bins to strings for JSON)
    risk_dist = df['churn_probability'].value_counts(bins=5, sort=False).to_dict()
    risk_dist = {f"{k.left:.2f}-{k.right:.2f}": v for k, v in risk_dist.items()}

    return {
        'total_customers': total,
        'churned_count': churned,
        'churn_rate': churn_rate,
        'store_summary': store_summary.to_dict('records'),
        'risk_distribution': risk_dist
    }

RFM_CSV_PATH = os.path.join(settings.BASE_DIR, 'raw_data', 'customer_rfm.csv')

def get_rfm_segments():
    """
    Read customer_rfm.csv and categorize customers into segments.
    Returns:
        - chart_data: For visualizing segment distribution.
        - summary_cards: Key metrics for each segment.
    """
    if not os.path.exists(RFM_CSV_PATH):
        return {'chart_data': {}, 'summary_cards': []}

    df = pd.read_csv(RFM_CSV_PATH)
    
    # Define Segments based on RFM Sum Score (Range 3-9)
    # R, F, M are 1-3. Total is 3-9.
    def assign_segment(row):
        score = row['rfm_score']
        r, f, m = row['r_score'], row['f_score'], row['m_score']
        
        if score >= 8:
            return "🏆 Champions"
        elif score >= 6:
            return "💎 Loyal Customers"
        elif r == 3 and f < 3:
            return "🆕 New Customers"
        elif r == 1 and f >= 2:
            return "⚠️ At Risk"
        else:
            return "💤 Hibernating"

    df['segment'] = df.apply(assign_segment, axis=1)
    
    # 1. Chart Data (Count per segment)
    counts = df['segment'].value_counts().to_dict()
    chart_data = {
        'labels': list(counts.keys()),
        'values': list(counts.values())
    }
    
    # 2. Summary Cards (Avg Monetary value per segment)
    avg_spend = df.groupby('segment')['monetary'].mean()
    summary_cards = [
        {'label': seg, 'count': counts[seg], 'avg_spend': f"${avg_spend[seg]:.2f}"}
        for seg in counts.keys()
    ]

    return {'chart_data': chart_data, 'summary_cards': summary_cards}