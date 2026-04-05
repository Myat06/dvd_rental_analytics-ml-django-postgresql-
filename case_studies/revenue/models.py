from django.db import models
from django.core.validators import MinValueValidator

class RevenueTransaction(models.Model):
    """
    Core model for revenue analytics.
    Supports OLAP queries via indexed fields and materialized views.
    """
    
    # Transaction type choices for clean filtering
    TYPE_CHOICES = [
        ('rental', 'Rental Income'),
        ('late_fee', 'Late Fee'),
        ('refund', 'Refund'),
        ('discount', 'Discount Applied'),
    ]
    
    # ─────────────────────────────────────────────────────────
    # Core Fields
    # ─────────────────────────────────────────────────────────
    transaction_id = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        help_text="Unique external transaction identifier"
    )
    
    date = models.DateField(
        db_index=True,
        help_text="Transaction date (used for time-series analytics)"
    )
    
    transaction_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES,
        db_index=True,
        help_text="Category of revenue transaction"
    )
    
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Transaction amount in USD"
    )
    
    # ─────────────────────────────────────────────────────────
    # Dimension Keys (denormalized for OLAP performance)
    # ─────────────────────────────────────────────────────────
    film_id = models.IntegerField(
        null=True, 
        blank=True, 
        db_index=True,
        help_text="Reference to film (denormalized for analytics)"
    )
    
    customer_id = models.IntegerField(
        null=True, 
        blank=True, 
        db_index=True,
        help_text="Reference to customer (denormalized for analytics)"
    )
    
    store_id = models.IntegerField(
        null=True, 
        blank=True, 
        db_index=True,
        help_text="Store location identifier"
    )
    
    # ─────────────────────────────────────────────────────────
    # Metadata
    # ─────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'revenue_transactions'
        verbose_name = 'Revenue Transaction'
        verbose_name_plural = 'Revenue Transactions'
        ordering = ['-date']  # Default: newest first
        
        # PostgreSQL-specific indexes for OLAP queries
        indexes = [
            # Composite index for time-series + type filtering
            models.Index(fields=['date', 'transaction_type']),
            # Index for film-level revenue analysis
            models.Index(fields=['film_id', 'date']),
            # Index for customer-level revenue analysis  
            models.Index(fields=['customer_id', 'date']),
            # Index for store performance reports
            models.Index(fields=['store_id', 'date']),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} | ${self.amount} | {self.transaction_type} | {self.date}"
    
    @property
    def is_income(self):
        """Quick helper: is this a positive revenue event?"""
        return self.transaction_type in ['rental', 'late_fee']
    
    @property
    def is_adjustment(self):
        """Quick helper: is this a negative/reducing event?"""
        return self.transaction_type in ['refund', 'discount']


class RevenueDailyStoreAgg(models.Model):
    """
    OLAP aggregate: daily revenue rolled up by store (drill-down slice).
    Refreshed after ETL from the fact table (RevenueTransaction).
    """

    agg_date = models.DateField(db_index=True)
    store_id = models.IntegerField(
        db_index=True,
        help_text="DVD store id; 0 if unknown in source data",
    )
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    transaction_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "revenue_olap_daily_store"
        verbose_name = "Revenue OLAP (daily × store)"
        verbose_name_plural = "Revenue OLAP (daily × store)"
        constraints = [
            models.UniqueConstraint(
                fields=["agg_date", "store_id"],
                name="uniq_revenue_olap_day_store",
            ),
        ]
        indexes = [
            models.Index(fields=["agg_date"]),
            models.Index(fields=["store_id", "agg_date"]),
        ]

    def __str__(self):
        return f"{self.agg_date} store={self.store_id} ${self.total_amount}"