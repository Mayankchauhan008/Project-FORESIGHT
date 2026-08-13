import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout


# ============================================================
# CREATE SEQUENCES
# ============================================================

def create_sequences(data, lookback=14):

    X = []
    y = []

    for i in range(
        lookback,
        len(data)
    ):

        X.append(
            data[i - lookback:i]
        )

        y.append(
            data[i]
        )

    return np.array(X), np.array(y)


# ============================================================
# LSTM FORECAST
# ============================================================

def lstm_forecast(
    df,
    date_col="date",
    target_col="quantity",
    periods=30,
    lookback=14,
    epochs=20,
    batch_size=32
):

    data = df[
        [date_col, target_col]
    ].copy()

    data[date_col] = pd.to_datetime(
        data[date_col]
    )

    series = (
        data
        .groupby(date_col)[target_col]
        .sum()
        .sort_index()
    )

    values = series.values.reshape(-1, 1)

    scaler = MinMaxScaler()

    scaled_values = scaler.fit_transform(
        values
    )

    X, y = create_sequences(
        scaled_values,
        lookback
    )

    if len(X) < 20:

        raise ValueError(
            "Not enough historical data "
            "for LSTM forecasting."
        )

    X = X.reshape(
        X.shape[0],
        X.shape[1],
        1
    )

    model = Sequential([

        LSTM(
            64,
            return_sequences=True,
            input_shape=(
                lookback,
                1
            )
        ),

        Dropout(0.2),

        LSTM(
            32
        ),

        Dropout(0.2),

        Dense(16),

        Dense(1)
    ])

    model.compile(
        optimizer="adam",
        loss="mse"
    )

    model.fit(
        X,
        y,
        epochs=epochs,
        batch_size=batch_size,
        verbose=0
    )

    current_sequence = (
        scaled_values[-lookback:]
        .reshape(1, lookback, 1)
    )

    predictions = []

    for _ in range(periods):

        prediction = model.predict(
            current_sequence,
            verbose=0
        )[0][0]

        predictions.append(
            prediction
        )

        current_sequence = np.append(
            current_sequence[:, 1:, :],
            [[[prediction]]],
            axis=1
        )

    predictions = np.array(
        predictions
    ).reshape(-1, 1)

    predictions = scaler.inverse_transform(
        predictions
    ).flatten()

    predictions = np.maximum(
        predictions,
        0
    )

    future_dates = pd.date_range(
        start=series.index.max()
        + pd.Timedelta(days=1),
        periods=periods,
        freq="D"
    )

    result = pd.DataFrame({

        date_col: future_dates,

        "forecast": predictions

    })

    return model, result