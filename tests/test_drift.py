import datetime

import pandas as pd
import pytest

from pathlib import Path
from scipy.stats import ks_2samp, chi2_contingency

ROOT = Path(__file__).resolve().parents[1]

REFERENCE_PATH = ROOT / "model_tracking" / "cars24-car-price-cleaned-new.csv"
MODELS_DIR = ROOT / "models"

NUMERIC_FEATURES = ["km_driven", "mileage", "age", "selling_price"]
CATEGORICAL_FEATURES = ["Petrol", "Diesel", "Electric"]
ALPHA = 0.05

TODAY = datetime.datetime.now().strftime("%d%m%y")  # ddmmyy
NEW_DATA_PATH = ROOT / "model_tracking" / f"{TODAY}_cars_24_price.csv"


@pytest.fixture(scope="module")
def reference_df():
    return pd.read_csv(REFERENCE_PATH)


@pytest.fixture(scope="module")
def new_df():
    return pd.read_csv(NEW_DATA_PATH)


def is_drifted(reference_df, new_df):
    """Return True if any numeric (KS) or categorical (Chi2) feature has drifted."""
    for col in NUMERIC_FEATURES:
        _, p_value = ks_2samp(reference_df[col], new_df[col])
        if p_value < ALPHA:
            return True

    for col in CATEGORICAL_FEATURES:
        table = pd.concat(
            [reference_df[col].value_counts(), new_df[col].value_counts()], axis=1
        ).fillna(0)
        _, p_value, _, _ = chi2_contingency(table)
        if p_value < ALPHA:
            return True

    return False


def test_new_model_created_when_drift_detected(reference_df, new_df):
    """If drift is detected, a model named ddmmyy_xgb_car_price_model must exist."""
    if not is_drifted(reference_df, new_df):
        pytest.skip("No drift detected, retraining not required")

    new_models = list(MODELS_DIR.glob(f"{TODAY}_xgb_car_price_model*.pkl"))
    assert new_models, (
        f"Drift detected but no model starting with '{TODAY}_xgb_car_price_model' "
        f"was found in {MODELS_DIR}"
    )
