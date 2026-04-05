from django.contrib import admin

from .models import RevenueDailyStoreAgg, RevenueTransaction


@admin.register(RevenueTransaction)
class RevenueTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "transaction_id",
        "date",
        "transaction_type",
        "amount",
        "film_id",
        "customer_id",
        "store_id",
    ]
    list_filter = ["transaction_type", "date", "store_id"]
    search_fields = ["transaction_id", "film_id", "customer_id"]
    date_hierarchy = "date"
    list_per_page = 100


@admin.register(RevenueDailyStoreAgg)
class RevenueDailyStoreAggAdmin(admin.ModelAdmin):
    list_display = ["agg_date", "store_id", "total_amount", "transaction_count"]
    list_filter = ["store_id"]
    date_hierarchy = "agg_date"
    ordering = ["-agg_date", "store_id"]