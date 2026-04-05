"""
Revenue ETL package: extract → transform → load → OLAP rollup refresh.
"""

from .pipeline import run_revenue_etl

__all__ = ['run_revenue_etl']
