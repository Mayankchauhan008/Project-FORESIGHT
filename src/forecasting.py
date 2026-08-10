import pandas as pd
import numpy as np


def prepare_time_series(
    df,
    date_column,
    target_column
):

    data = df.copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data[target_column] = pd.to_numeric(
        data[target_column],
        errors="coerce"
    )

    data = data.dropna(
        subset=[
            date_column,
            target_column
        ]
    )

    data = (
        data
        .groupby(date_column)[target_column]
        .sum()
        .reset_index()
        .sort_values(date_column)
    )

    return data


def moving_average_forecast(
    data,
    target_column,
    forecast_days=30,
    window=7
):

    data = data.copy()

    if len(data) < window:

        raise ValueError(
            "Not enough historical data."
        )

    average_value = (
        data[target_column]
        .tail(window)
        .mean()
    )

    last_date = data.index[-1]

    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=forecast_days,
        freq="D"
    )

    forecast = pd.DataFrame({

        "date": future_dates,

        "forecast": average_value

    })

    return forecast


def calculate_metrics(
    actual,
    predicted
):

    actual = np.asarray(actual)

    predicted = np.asarray(predicted)

    mae = np.mean(
        np.abs(
            actual - predicted
        )
    )

    rmse = np.sqrt(
        np.mean(
            (actual - predicted) ** 2
        )
    )

    non_zero = actual != 0

    if non_zero.any():

        mape = np.mean(
            np.abs(
                (
                    actual[non_zero]
                    -
                    predicted[non_zero]
                )
                /
                actual[non_zero]
            )
        ) * 100

    else:

        mape = 0

    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape
    }