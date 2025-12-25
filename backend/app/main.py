from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.explain import router as explain_router
from app.api.ai_insights import router as ai_insights_router

from app.api.upload import router as upload_router
from app.api.datasets import router as datasets_router
from app.api.profile import router as profile_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(datasets_router)
app.include_router(profile_router)
app.include_router(explain_router)
app.include_router(ai_insights_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
