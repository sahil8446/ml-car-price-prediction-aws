import pandas as pd
from pathlib import Path
from scipy.stats import ks_2samp, chi2_contingency

ROOT = Path(__file__).resolve().parents[1]

REFERENCE_PATH = ROOT / "data" / "cars24-car-price-cleaned-new.csv"

NUMERIC_FEATURES = ["km_driven", "mileage", "age", "selling_price"]
CATEGORICAL_FEATURES = ["Petrol", "Diesel", "Electric"]
ALPHA = 0.05


def is_drifted(reference_df, new_df):
    """Return True if any numeric (KS) or categorical (Chi2) feature has drifted."""
    for col in NUMERIC_FEATURES:
        _, p_value = ks_2samp(reference_df[col], new_df[col])
        if p_value < ALPHA:
            return True

    for col in CATEGORICAL_FEATURES:
        table = pd.concat(
            [
                reference_df[col].value_counts(),
                new_df[col].value_counts(),
            ],
            axis=1,
        ).fillna(0)

        _, p_value, _, _ = chi2_contingency(table)
        if p_value < ALPHA:
            return True

    return False


def test_reference_dataset_exists():
    """Verify that the reference dataset is available."""
    assert REFERENCE_PATH.exists(), (
        f"Reference dataset not found: {REFERENCE_PATH}"
    )


def test_no_drift_in_identical_data():
    """Identical datasets should not trigger drift detection."""
    reference_df = pd.read_csv(REFERENCE_PATH)

    assert not is_drifted(reference_df, reference_df.copy())


def test_drift_detected_in_modified_data():
    """A substantial shift in a numeric feature should trigger drift detection."""
    reference_df = pd.read_csv(REFERENCE_PATH)
    new_df = reference_df.copy()

    # Introduce a substantial shift in selling prices.
    new_df["selling_price"] = new_df["selling_price"] * 10

    assert is_drifted(reference_df, new_df)