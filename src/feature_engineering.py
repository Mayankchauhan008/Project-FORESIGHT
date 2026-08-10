import pandas as pd
import numpy as np


def add_date_features(
    df,
    date_column
):

    df = df.copy()

    if date_column not in df.columns:
        return df

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    df["year"] = df[date_column].dt.year

    df["month"] = df[date_column].dt.month

    df["day"] = df[date_column].dt.day

    df["day_of_week"] = (
        df[date_column].dt.dayofweek
    )

    df["quarter"] = (
        df[date_column].dt.quarter
    )

    df["week_of_year"] = (
        df[date_column]
        .dt.isocalendar()
        .week
        .astype("float")
    )

    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    return df


def add_lag_features(
    df,
    target_column,
    lags=(1, 7, 14, 30)
):

    df = df.copy()

    if target_column not in df.columns:
        return df

    for lag in lags:

        df[f"{target_column}_lag_{lag}"] = (
            df[target_column]
            .shift(lag)
        )

    return df


def add_rolling_features(
    df,
    target_column,
    windows=(7, 14, 30)
):

    df = df.copy()

    if target_column not in df.columns:
        return df

    for window in windows:

        df[
            f"{target_column}_rolling_mean_{window}"
        ] = (
            df[target_column]
            .rolling(window)
            .mean()
        )

        df[
            f"{target_column}_rolling_std_{window}"
        ] = (
            df[target_column]
            .rolling(window)
            .std()
        )

    return df


def create_features(
    df,
    date_column=None,
    target_column=None
):

    df = df.copy()

    if date_column:

        df = add_date_features(
            df,
            date_column
        )

    if target_column:

        df = add_lag_features(
            df,
            target_column
        )

        df = add_rolling_features(
            df,
            target_column
        )

    return df