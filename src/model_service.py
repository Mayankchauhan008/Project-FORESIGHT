from pathlib import Path
import joblib
import pandas as pd
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_DIR = Path("C:/Users/mayank/OneDrive/Desktop/Project-FORESIGHT/models")


class ModelService:

    def __init__(self):

        self.random_forest = None
        self.xgboost = None
        self.scaler = None

        self.load_models()


    def load_models(self):

        rf_path = (
            MODEL_DIR /
            "random_forest.pkl"
        )

        xgb_path = (
            MODEL_DIR /
            "xgboost.pkl"
        )

        scaler_path = (
            MODEL_DIR /
            "scaler.pkl"
        )

        if rf_path.exists():

            self.random_forest = (
                joblib.load(rf_path)
            )

        if xgb_path.exists():

            self.xgboost = (
                joblib.load(xgb_path)
            )

        if scaler_path.exists():

            self.scaler = (
                joblib.load(scaler_path)
            )


    def get_model(
        self,
        model_name="xgboost"
    ):

        if model_name.lower() == "random_forest":

            return self.random_forest

        return self.xgboost


    def predict(
        self,
        features,
        model_name="xgboost"
    ):

        model = self.get_model(
            model_name
        )

        if model is None:

            raise ValueError(
                f"{model_name} model is not available."
            )

        if isinstance(
            features,
            pd.DataFrame
        ):

            X = features.copy()

        else:

            X = np.asarray(
                features
            )

        if self.scaler is not None:

            try:

                X = self.scaler.transform(X)

            except Exception:

                # Some tree-based models
                # may already expect raw features.
                pass

        prediction = model.predict(X)

        return prediction