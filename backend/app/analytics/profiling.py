from __future__ import annotations

import pandas as pd


def profile_dataframe(df: pd.DataFrame) -> dict:
    # Basic dataset info
    n_rows, n_cols = df.shape

    # Column types (string representation)
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # Missingness
    missing_count = df.isna().sum()
    missing_pct = (missing_count / max(n_rows, 1) * 100).round(2)

    missing = {
        col: {
            "missing_count": int(missing_count[col]),
            "missing_pct": float(missing_pct[col]),
        }
        for col in df.columns
    }

    # Numeric summary
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    numeric_summary = {}
    if numeric_cols:
        desc = df[numeric_cols].describe().T  # count, mean, std, min, 25%, 50%, 75%, max
        for col in numeric_cols:
            numeric_summary[col] = {
                "count": int(desc.loc[col, "count"]),
                "mean": float(desc.loc[col, "mean"]),
                "std": float(desc.loc[col, "std"]) if pd.notna(desc.loc[col, "std"]) else None,
                "min": float(desc.loc[col, "min"]),
                "max": float(desc.loc[col, "max"]),
            }

    # Categorical preview (top 5 values)
    categorical_cols = [c for c in df.columns if c not in numeric_cols]
    categorical_top_values = {}
    for col in categorical_cols:
        vc = df[col].astype("string").value_counts(dropna=False).head(5)
        categorical_top_values[col] = [
            {"value": None if pd.isna(idx) else str(idx), "count": int(cnt)}
            for idx, cnt in vc.items()
        ]

    return {
        "shape": [int(n_rows), int(n_cols)],
        "dtypes": dtypes,
        "missing": missing,
        "numeric_summary": numeric_summary,
        "categorical_top_values": categorical_top_values,
    }
