"""Functions the report uses. Keep the report readable by moving longer code here."""

import pandas as pd


def summarise_by(df: pd.DataFrame, group: str, value: str) -> pd.DataFrame:
    """Count, mean and standard deviation of `value` for each level of `group`."""
    return (
        df.groupby(group)[value]
        .agg(n="count", mean="mean", sd="std")
        .round(1)
        .reset_index()
    )
