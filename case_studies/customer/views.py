from django.shortcuts import render
from . import analytics
import json

def customer_overview(request):
    # 1. Get churn stats
    churn_stats = analytics.get_dashboard_stats()
    
    # 2. Get RFM segments
    rfm_data = analytics.get_rfm_segments()
    
    # 3. Build chart_json with EXACT keys JS expects
    chart_data = {
        # Store churn chart
        'store_labels': [f"Store {int(r['store_id'])}" for r in churn_stats['store_summary']],
        'store_churn_rates': [float(r['churn_rate']) for r in churn_stats['store_summary']],
        
        # Risk distribution chart
        'risk_labels': list(churn_stats['risk_distribution'].keys()),
        'risk_counts': [int(v) for v in churn_stats['risk_distribution'].values()],
        
        # RFM chart
        'rfm_labels': rfm_data['chart_data'].get('labels', []),
        'rfm_counts': [int(v) for v in rfm_data['chart_data'].get('values', [])],
    }
    
    context = {
        'stats': churn_stats,
        'rfm': rfm_data,
        'chart_json': json.dumps(chart_data),
    }
    return render(request, 'customer/overview.html', context)