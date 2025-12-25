from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException

from app.analytics.profiling import profile_dataframe
from app.api.datasets import read_csv_safely

router = APIRouter()

DATASETS_DIR = Path(__file__).resolve().parents[1] / "storage" / "datasets"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


@router.post("/datasets/{dataset_id}/explain")
async def explain_dataset_profile(dataset_id: str):
    file_path = DATASETS_DIR / f"{dataset_id}.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = read_csv_safely(file_path)
    prof = profile_dataframe(df)

    prompt = f"""
You are an analytics assistant. Explain the dataset profile in plain English.
Be concise, practical, and structured.

What to include:
1) What the dataset looks like (rows, columns)
2) Which columns are numeric vs categorical (based on dtypes)
3) Any missing values concerns
4) Notable patterns from numeric summary (ranges, outliers hints)
5) What analyses the user should do next (3-5 suggestions)

Here is the dataset profile JSON:
{prof}
""".strip()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        },
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

    return {
        "dataset_id": dataset_id,
        "model": OLLAMA_MODEL,
        "explanation": text,
    }
