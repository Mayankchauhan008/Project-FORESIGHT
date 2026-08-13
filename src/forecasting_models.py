import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error
)

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(actual, predicted):
    """
    Calculate forecasting evaluation metrics.
    """

    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    # Avoid division by zero
    denominator = np.where(actual == 0, 1, np.abs(actual))

    mape = np.mean(
        np.abs((actual - predicted) / denominator)
    ) * 100

    return {
        "MAE": round(float(mae), 4),
        "RMSE": round(float(rmse), 4),
        "MAPE": round(float(mape), 4)
    }


# ============================================================
# PROPHET
# ============================================================

def prophet_forecast(
    df,
    date_col="date",
    target_col="quantity",
    periods=30
):
    """
    Prophet demand forecasting.
    """

    try:
        from prophet import Prophet
    except ImportError:
        raise ImportError(
            "Prophet is not installed. "
            "Run: pip install prophet"
        )

    data = df[[date_col, target_col]].copy()

    data[date_col] = pd.to_datetime(data[date_col])

    data = (
        data
        .groupby(date_col)[target_col]
        .sum()
        .reset_index()
    )

    data.columns = ["ds", "y"]

    data = data.sort_values("ds")

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False
    )

    model.fit(data)

    future = model.make_future_dataframe(
        periods=periods,
        freq="D"
    )

    forecast = model.predict(future)

    result = forecast[
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ].copy()

    result.rename(
        columns={"ds": date_col},
        inplace=True
    )

    return model, result


# ============================================================
# ARIMA
# ============================================================

def arima_forecast(
    df,
    date_col="date",
    target_col="quantity",
    order=(7, 1, 2),
    periods=30
):
    """
    ARIMA forecasting.

    p = autoregressive lag
    d = differencing
    q = moving average
    """

    data = df[[date_col, target_col]].copy()

    data[date_col] = pd.to_datetime(data[date_col])

    series = (
        data
        .groupby(date_col)[target_col]
        .sum()
        .sort_index()
    )

    model = ARIMA(
        series,
        order=order
    )

    fitted_model = model.fit()

    forecast = fitted_model.forecast(
        steps=periods
    )

    future_dates = pd.date_range(
        start=series.index.max() + pd.Timedelta(days=1),
        periods=periods,
        freq="D"
    )

    result = pd.DataFrame({
        date_col: future_dates,
        "forecast": forecast.values
    })

    result["forecast"] = result["forecast"].clip(
        lower=0
    )

    return fitted_model, result


# ============================================================
# SARIMA
# ============================================================

def sarima_forecast(
    df,
    date_col="date",
    target_col="quantity",
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 7),
    periods=30
):
    """
    SARIMA forecasting.

    order = (p, d, q)
    seasonal_order = (P, D, Q, s)

    s = seasonal period
    """

    data = df[[date_col, target_col]].copy()

    data[date_col] = pd.to_datetime(data[date_col])

    series = (
        data
        .groupby(date_col)[target_col]
        .sum()
        .sort_index()
    )

    model = SARIMAX(
        series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    fitted_model = model.fit(
        disp=False
    )

    forecast = fitted_model.forecast(
        steps=periods
    )

    future_dates = pd.date_range(
        start=series.index.max() + pd.Timedelta(days=1),
        periods=periods,
        freq="D"
    )

    result = pd.DataFrame({
        date_col: future_dates,
        "forecast": forecast.values
    })

    result["forecast"] = result["forecast"].clip(
        lower=0
    )

    return fitted_model, result


# ============================================================
# MODEL COMPARISON
# ============================================================

def compare_forecasts(
    actual,
    predictions
):
    """
    Compare multiple forecasting models.

    predictions example:

    {
        "ARIMA": [...],
        "SARIMA": [...],
        "LSTM": [...]
    }
    """

    results = []

    for model_name, predicted in predictions.items():

        metrics = calculate_metrics(
            actual,
            predicted
        )

        metrics["Model"] = model_name

        results.append(metrics)

    result_df = pd.DataFrame(results)

    result_df = result_df[
        ["Model", "MAE", "RMSE", "MAPE"]
    ]

    result_df = result_df.sort_values(
        "RMSE"
    )

    return result_df.reset_index(
        drop=True
    )