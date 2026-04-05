from django.shortcuts import render

from case_studies.revenue.analytics import get_revenue_kpis
from case_studies.revenue import predict


def home(request):
    kpis = get_revenue_kpis()
    forecast_status = predict.forecast_status(7)
    if forecast_status["available"]:
        forecast_status["next_7d_forecast_total"] = forecast_status.get("next_forecast_total", 0)
    context = {
        "kpis": kpis,
        "forecast_status": forecast_status,
    }
    return render(request, "dashboard/home.html", context)