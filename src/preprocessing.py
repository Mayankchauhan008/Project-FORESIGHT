import pandas as pd
import numpy as np

from .utils import clean_column_names


def remove_duplicates(df):

    df = df.copy()

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    print(f"Removed {removed} duplicate rows.")

    return df


def handle_missing_values(df):

    df = df.copy()

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    categorical_columns = df.select_dtypes(
        exclude=np.number
    ).columns

    for col in numeric_columns:

        df[col] = df[col].fillna(
            df[col].median()
        )

    for col in categorical_columns:

        mode = df[col].mode()

        if not mode.empty:

            df[col] = df[col].fillna(
                mode.iloc[0]
            )

    return df


def convert_numeric_columns(df):

    df = df.copy()

    for col in df.columns:

        if df[col].dtype == "object":

            converted = pd.to_numeric(
                df[col],
                errors="coerce"
            )

            if converted.notna().mean() > 0.8:

                df[col] = converted

    return df


def preprocess_dataframe(df):

    df = clean_column_names(df)

    df = remove_duplicates(df)

    df = convert_numeric_columns(df)

    df = handle_missing_values(df)

    return df