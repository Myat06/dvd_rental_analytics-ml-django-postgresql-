from django.db import models

class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    store_id = models.IntegerField()
    address_id = models.IntegerField()
    active = models.BooleanField()
    create_date = models.DateTimeField()

    class Meta:
        db_table = 'customer'
        managed = False  # Already exists in Neon sample DB


class FactCustomerBehavior(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    store_id = models.IntegerField()
    active = models.BooleanField()
    total_rentals = models.IntegerField()
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)
    avg_rental_duration = models.DecimalField(max_digits=10, decimal_places=2)
    days_since_last_rental = models.IntegerField()
    last_rental_date = models.DateField()
    is_churn = models.BooleanField(default=False)

    class Meta:
        db_table = 'fact_customer_behavior'


class StoreChurnSummary(models.Model):
    store_id = models.IntegerField(primary_key=True)
    total_customers = models.IntegerField()
    churned_customers = models.IntegerField()
    churn_rate = models.DecimalField(max_digits=5, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'store_churn_summary'


class ModelInfo(models.Model):
    model_name = models.CharField(max_length=100)
    model_file = models.CharField(max_length=255)
    training_data = models.CharField(max_length=255)
    training_date = models.DateTimeField()
    model_summary = models.TextField(blank=True)

    def __str__(self):
        return f"{self.model_name} - {self.training_date.strftime('%Y-%m-%d')}"