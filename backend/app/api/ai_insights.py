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

@router.post("/datasets/{dataset_id}/feature-ideas")
async def feature_engineering_ideas(dataset_id: str):
    file_path = DATASETS_DIR / f"{dataset_id}.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = read_csv_safely(file_path)
    prof = profile_dataframe(df)

    # send small samples per column (helps LLM suggest realistic features)
    samples = {}
    for col in df.columns:
        vals = df[col].dropna().head(8).astype("string").tolist()
        samples[col] = vals

    prompt = f"""
You are an analytics assistant. Suggest feature engineering ideas for this dataset.

Rules:
- Be practical. Assume this dataset could be used for prediction or segmentation.
- Use the column names, dtypes, and sample values.
- Return both:
  A) A human-readable plan (bullets)
  B) A small JSON "feature_plan" that lists suggested engineered features.

Include sections:
1) Type fixes (date parsing, numeric casting)
2) Missing value handling strategies
3) Categorical encoding suggestions
4) Numeric transforms (log, scaling, binning, outliers)
5) Time-based features (if any date column exists)
6) Interaction features (2-4 realistic combos)
7) Target leakage warnings (if any column looks like an ID or label)

Dataset profile JSON:
{prof}

Sample values per column (JSON):
{samples}

Output format:
- First: a clean bulleted plan with headings
- Then: a JSON block with key "feature_plan" that is valid JSON (no comments)

Keep it concise but useful.
""".strip()

    text = await call_ollama(prompt)
    return {"dataset_id": dataset_id, "model": OLLAMA_MODEL, "ideas": text}

@router.post("/datasets/{dataset_id}/modeling-suggestions")
async def modeling_suggestions(dataset_id: str):
    file_path = DATASETS_DIR / f"{dataset_id}.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = read_csv_safely(file_path)
    prof = profile_dataframe(df)

    samples = {}
    for col in df.columns:
        samples[col] = df[col].dropna().head(5).astype("string").tolist()

    prompt = f"""
You are a senior data scientist.

Based on the dataset profile and sample values below, provide modeling guidance.

Include sections:
1) Problem framing (classification, regression, clustering, etc.)
2) Potential target variable(s) and justification
3) Baseline models to start with
4) More advanced models (if data supports it)
5) Recommended evaluation metrics
6) Validation strategy (train/test split, cross-validation, time-based split)
7) Key risks and pitfalls (imbalance, leakage, small data, bias)

Dataset profile (JSON):
{prof}

Sample values (JSON):
{samples}

Be practical and concise. Assume the user wants to build a real model.
""".strip()

    text = await call_ollama(prompt)
    return {
        "dataset_id": dataset_id,
        "model": OLLAMA_MODEL,
        "suggestions": text,
    }
