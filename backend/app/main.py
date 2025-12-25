from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.datasets import router as datasets_router
from app.api.profile import router as profile_router

app = FastAPI()

app.include_router(upload_router)
app.include_router(datasets_router)
app.include_router(profile_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
