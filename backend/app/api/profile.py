from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.analytics.profiling import profile_dataframe

router = APIRouter()

DATASETS_DIR = Path(__file__).resolve().parents[1] / "storage" / "datasets"


@router.get("/datasets/{dataset_id}/profile")
def profile_dataset(dataset_id: str):
    file_path = DATASETS_DIR / f"{dataset_id}.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = pd.read_csv(file_path)
    result = profile_dataframe(df)

    return {"dataset_id": dataset_id, **result}
