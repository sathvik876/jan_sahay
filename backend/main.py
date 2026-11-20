# backend/main.py

import uvicorn
from fastapi import FastAPI
from backend.app.api import router as api_router
from backend.app.db import Base, engine
from backend.app import models

app = FastAPI(title="JanSahay AI Backend")
app.include_router(api_router, prefix="")
app.include_router(api_router, prefix="/api")

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
