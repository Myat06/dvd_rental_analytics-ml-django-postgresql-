import json

from django.shortcuts import render

from . import analytics
from . import predict


def revenue_overview(request):
    days = int(request.GET.get("days", 30))
    predict_days = int(request.GET.get("predict_days", 7))

    kpis = analytics.get_revenue_kpis(days=days)
    trend_data = analytics.get_revenue_trend(days=days)
    category_data = analytics.get_revenue_by_category(days=days)
    weekday_data = analytics.get_revenue_by_weekday(days=days)
    forecast = predict.predict_next_days(predict_days)

    chart_data = {
        "trend": {
            "dates": [x["date"] for x in trend_data],
            "amounts": [x["amount"] for x in trend_data],
        },
        "categories": {
            "labels": [x["category"] for x in category_data],
            "amounts": [x["amount"] for x in category_data],
        },
        "weekdays": {
            "labels": [x["day"] for x in weekday_data],
            "amounts": [x["amount"] for x in weekday_data],
        },
        "forecast": (
            {
                "dates": forecast["dates"],
                "amounts": forecast["amounts"],
                "meta": forecast["meta"],
            }
            if forecast
            else None
        ),
    }

    context = {
        "kpis": kpis,
        "chart_json": json.dumps(chart_data),
        "selected_days": days,
        "days_options": [30, 60, 90],
        "selected_predict_days": predict_days,
        "predict_days_options": [7, 30, 60],
        "forecast_status": predict.forecast_status(predict_days),
    }
    return render(request, "revenue/overview.html", context)