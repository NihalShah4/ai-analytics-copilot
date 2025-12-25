from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()

DATASETS_DIR = Path(__file__).resolve().parents[1] / "storage" / "datasets"


@router.get("/datasets/{dataset_id}/preview")
def preview_dataset(dataset_id: str, n: int = 5):
    file_path = DATASETS_DIR / f"{dataset_id}.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found.")

    if n < 1 or n > 50:
        raise HTTPException(status_code=400, detail="n must be between 1 and 50.")

    df = pd.read_csv(file_path)

    preview_df = df.head(n)
    return {
        "dataset_id": dataset_id,
        "shape": [int(df.shape[0]), int(df.shape[1])],
        "columns": df.columns.tolist(),
        "preview": preview_df.to_dict(orient="records"),
    }
