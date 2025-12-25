from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException

from app.analytics.profiling import profile_dataframe
from app.api.datasets import read_csv_safely

router = APIRouter()

DATASETS_DIR = Path(__file__).resolve().parents[1] / "storage" / "datasets"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


async def call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(OLLAMA_URL, json=payload)
            r.raise_for_status()
            data = r.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Ollama is not reachable. Make sure Ollama is installed and running.",
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ollama call failed: {str(e)}")

    text = (data.get("response") or "").strip()
    if not text:
        raise HTTPException(status_code=502, detail="Empty response from Ollama.")
    return text


@router.get("/datasets/{dataset_id}/columns")
def list_columns(dataset_id: str):
    file_path = DATASETS_DIR / f"{dataset_id}.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df = read_csv_safely(file_path)
    return {"dataset_id": dataset_id, "columns": df.columns.tolist()}


@router.post("/datasets/{dataset_id}/explain-column")
async def explain_column(dataset_id: str, column: str):
    file_path = DATASETS_DIR / f"{dataset_id}.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = read_csv_safely(file_path)
    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Unknown column: {column}")

    prof = profile_dataframe(df)

    # Lightweight column stats (avoid sending whole dataset)
    s = df[column]
    sample_values = s.dropna().head(10).astype("string").tolist()

    prompt = f"""
You are an analytics assistant. Explain this dataset column in plain English.

Column name: {column}
Column dtype: {str(df[column].dtype)}

Dataset profile summary (JSON):
{prof}

Sample values from this column (first 10 non-null):
{sample_values}

Explain:
1) What this column likely represents (based on name + sample values)
2) Quality checks to run (missing, duplicates, invalid ranges, weird categories)
3) How this column could be used in analysis/modeling
4) Any cautions (leakage, ID-like columns, encoding issues)

Keep it practical and structured in bullets.
""".strip()

    explanation = await call_ollama(prompt)
    return {"dataset_id": dataset_id, "column": column, "explanation": explanation}
