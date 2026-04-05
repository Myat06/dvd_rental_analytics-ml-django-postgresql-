# Generated manually for OLAP aggregate table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("revenue", "0002_alter_revenuetransaction_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="RevenueDailyStoreAgg",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("agg_date", models.DateField(db_index=True)),
                (
                    "store_id",
                    models.IntegerField(
                        db_index=True,
                        help_text="DVD store id; 0 if unknown in source data",
                    ),
                ),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("transaction_count", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Revenue OLAP (daily × store)",
                "verbose_name_plural": "Revenue OLAP (daily × store)",
                "db_table": "revenue_olap_daily_store",
            },
        ),
        migrations.AddConstraint(
            model_name="revenuedailystoreagg",
            constraint=models.UniqueConstraint(
                fields=("agg_date", "store_id"),
                name="uniq_revenue_olap_day_store",
            ),
        ),
        migrations.AddIndex(
            model_name="revenuedailystoreagg",
            index=models.Index(fields=["agg_date"], name="revenue_ola_agg_dat_7a8b2c_idx"),
        ),
        migrations.AddIndex(
            model_name="revenuedailystoreagg",
            index=models.Index(
                fields=["store_id", "agg_date"],
                name="revenue_ola_store_i_9d0e1f_idx",
            ),
        ),
    ]
