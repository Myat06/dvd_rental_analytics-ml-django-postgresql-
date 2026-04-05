from django.core.management.base import BaseCommand

from data_pipeline.revenue.pipeline import run_revenue_etl


class Command(BaseCommand):
    help = (
        "Run revenue ETL: extract from PostgreSQL (payment chain) → transform → "
        "load into revenue_transactions → refresh OLAP daily×store aggregates."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            default=None,
            help="Optional path (reserved); extract uses the DVD rental DB.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting revenue ETL pipeline..."))
        try:
            loaded, olap_rows, csv_path = run_revenue_etl(options["source"])
            self.stdout.write(
                self.style.SUCCESS(
                    f"ETL complete: {loaded} fact rows loaded, {olap_rows} OLAP aggregate rows.\n"
                    f"CSV explicitly saved to: {csv_path}"
                )
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"ETL failed: {e}"))
            raise