# backend/main.py

import uvicorn
from fastapi import FastAPI

if __package__:
    from .app import models
    from .app.api import router as api_router
    from .app.db import Base, engine
else:
    from app import models
    from app.api import router as api_router
    from app.db import Base, engine

app = FastAPI(title="JanSahay AI Backend")
app.include_router(api_router, prefix="")
app.include_router(api_router, prefix="/api")

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    app_target = "backend.main:app" if __package__ else "main:app"
    uvicorn.run(app_target, host="0.0.0.0", port=8000, reload=True)
