# DVD Analytics - Cinemetrics Group Project

## 🎥 Overview
Django app for DVD rental revenue analytics, ETL pipeline, and ML forecasting. Features dashboard with KPIs, revenue OLAP, daily revenue prediction.

## 🚀 Quick Start for Team Members

### 1. Clone & Environment
```
git clone <repo-url>
cd dvd_analytics
python -m venv venv
# Windows:
venv\\Scripts\\activate
# Mac/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

### 2. PostgreSQL Setup (Required for ETL)
**Windows Install:**
- Download [PostgreSQL 16 installer](https://www.postgresql.org/download/windows/) (pgAdmin included).
- Run installer, set **superuser password** (remember it!).
- Default port 5432, localhost.

**Create Database & Load Sample Data:**
- Open pgAdmin, connect to server.
- Create database `dvdrental`:
  ```
  CREATE DATABASE dvdrental;
  ```
- Download [dvdrental sample DB backup](https://github.com/postgres-samples/dvdrental/releases) or SQL dump from [pgfoundry](http://www.postgresqltutorial.com/load-dvdrental-database/).
- Right-click dvdrental DB > Restore > select dump file (dvdrental.tar or .sql).

**Alternative: SQL script execution:**
```
psql -U postgres -h localhost -p 5432 -d dvdrental -f dvdrental.sql
```

### 3. Environment Variables (.env)
```
cp .env.example .env
# Edit .env with your DB details
```

**Current hardcoded in settings.py (update manually or use .env after changes):**
```
DB_NAME=dvdrental
DB_USER=postgres
DB_PASSWORD=myatmin123thu45  # Change this!
DB_HOST=localhost
DB_PORT=5432
```

### 4. Django Setup
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 5. Load Data & Analytics
```
python manage.py run_revenue_etl
# Views: http://127.0.0.1:8000/
# Admin: http://127.0.0.1:8000/admin/ (create superuser first)
```

## 🔧 Development
- Data pipeline: `data_pipeline/revenue/`
- Dashboard: `dashboard/views.py`
- ML Forecast: `case_studies/revenue/predict.py` (trains on loaded data)
- ML models saved to `media/ml_models/`

## 📋 Security Note
- Update DB password in `dvd_analytics/settings.py`.
- Add to `.gitignore`: `.env`, `venv/`, `*.csv` (raw_data optional).

Happy analyzing! 🎞️
