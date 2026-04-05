"""
Refresh OLAP aggregate tables from the revenue fact table (RevenueTransaction).
"""

import logging
from django.db.models import Sum, Count

from case_studies.revenue.models import RevenueDailyStoreAgg, RevenueTransaction

logger = logging.getLogger(__name__)


def refresh_revenue_daily_olap() -> int:
    """
    Rebuild daily×store rollups. Safe to run after each ETL load.
    Returns number of aggregate rows written.
    """
    logger.info("Refreshing revenue OLAP (daily × store)...")
    RevenueDailyStoreAgg.objects.all().delete()
    if not RevenueTransaction.objects.exists():
        logger.warning("No fact rows; OLAP table left empty.")
        return 0

    rows = []
    for r in (
        RevenueTransaction.objects.values("date", "store_id")
        .annotate(total=Sum("amount"), n=Count("id"))
        .order_by("date", "store_id")
    ):
        sid = r["store_id"] if r["store_id"] is not None else 0
        rows.append(
            RevenueDailyStoreAgg(
                agg_date=r["date"],
                store_id=sid,
                total_amount=r["total"],
                transaction_count=r["n"],
            )
        )

    RevenueDailyStoreAgg.objects.bulk_create(rows, batch_size=2000)
    logger.info("OLAP refresh complete: %s aggregate rows", len(rows))
    return len(rows)
