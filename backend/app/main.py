from fastapi import FastAPI

from app.api.upload import router as upload_router

app = FastAPI()

app.include_router(upload_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
