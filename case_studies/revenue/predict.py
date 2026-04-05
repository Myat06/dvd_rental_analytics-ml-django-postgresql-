import os
import datetime
import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, explained_variance_score

# Paths resolution compatible with standalone and Django execution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, 'raw_data', 'revenue_clean.csv')

def _train_memory_model():
    if not os.path.exists(CSV_PATH):
        return None

    df = pd.read_csv(CSV_PATH)
    if df.empty:
        return None
        
    df['date'] = pd.to_datetime(df['date'])
    daily_revenue = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
    daily_revenue = daily_revenue.sort_values('date')
    
    if len(daily_revenue) < 14:
        return None

    X = []
    y = []
    for _, row in daily_revenue.iterrows():
        d = row['date']
        X.append([d.toordinal(), d.weekday()])
        y.append(row['amount'])
        
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)

    split_idx = int(len(X) * 0.8)
    X_train, y_train = X[:split_idx], y[:split_idx]
    X_test, y_test = X[split_idx:], y[split_idx:]

    model = LinearRegression()
    model.fit(X_train, y_train)

    mae_train = mean_absolute_error(y_train, model.predict(X_train))
    mae_test = mean_absolute_error(y_test, model.predict(X_test))
    r2_train = r2_score(y_train, model.predict(X_train))
    r2_test = r2_score(y_test, model.predict(X_test))
    accuracy_test = explained_variance_score(y_test, model.predict(X_test))

    return {
        "model": model, 
        "daily_revenue": daily_revenue,
        "metrics": {
            "trained_at": datetime.date.today().isoformat(),
            "train_days": len(X),
            "mae_train": mae_train,
            "mae_test": mae_test,
            "r2_train": r2_train,
            "r2_test": r2_test,
            "accuracy_test": accuracy_test
        }
    }

def predict_next_days(n_days=7):
    trained = _train_memory_model()
    if trained is None:
        return None
        
    model = trained["model"]
    daily_revenue = trained["daily_revenue"]
    
    last_date = daily_revenue.iloc[-1]['date']
    
    labels = []
    values = []
    
    for k in range(1, n_days + 1):
        future_date = last_date + timedelta(days=k)
        labels.append(future_date.isoformat())
        x_future = np.array([[future_date.toordinal(), future_date.weekday()]], dtype=float)
        values.append(float(model.predict(x_future)[0]))
        
    return {
        "dates": labels,
        "amounts": values,
        "meta": trained["metrics"]
    }

def forecast_status(predict_days=7):
    predictions = predict_next_days(predict_days)
    if not predictions:
        return {"available": False, "message": "Not enough data in CSV to generate forecast."}
        
    total_forecast = sum(predictions["amounts"])
    meta = predictions["meta"]
    
    return {
        "available": True,
        "predict_days": predict_days,
        "trained_at": meta.get("trained_at"),
        "mae_train": meta.get("mae_train"),
        "mae_test": meta.get("mae_test"),
        "r2_train": meta.get("r2_train"),
        "r2_test": meta.get("r2_test"),
        "next_forecast_total": round(total_forecast, 2),
    }

def main():
    predictions = predict_next_days(7)
    if not predictions:
        print("Error: Could not train model. Is the CSV missing or under 14 rows?")
        return
        
    meta = predictions["meta"]
    print("=================== IN-MEMORY MODEL METRICS ===================")
    print(f"Algorithm: Linear Regression")
    print(f"MAE (Train): ${meta['mae_train']:.2f} | MAE (Test): ${meta['mae_test']:.2f}")
    print(f"R² (Train):  {meta['r2_train']:.3f} | R² (Test):  {meta['r2_test']:.3f}")
    print(f"Accuracy (Test): {meta['accuracy_test']:.3f}")
    print("===============================================================\n")

    print(f"--- 7-DAY FORECAST ---")
    for i in range(len(predictions["dates"])):
        print(f" > {predictions['dates'][i]}: ${predictions['amounts'][i]:.2f}")
        
    total = sum(predictions["amounts"])
    print(f"---------------------------------------------------------------")
    print(f"TOTAL PREDICTED VALUE FOR NEXT 7 DAYS: ${total:.2f}")
    print(f"---------------------------------------------------------------")

if __name__ == "__main__":
    main()

