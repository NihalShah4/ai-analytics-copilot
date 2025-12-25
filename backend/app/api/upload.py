from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

DATASETS_DIR = Path(__file__).resolve().parents[1] / "storage" / "datasets"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")

    dataset_id = str(uuid4())
    save_path = DATASETS_DIR / f"{dataset_id}.csv"

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    save_path.write_bytes(content)

    return {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "saved_as": save_path.name,
    }
