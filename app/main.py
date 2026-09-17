from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.files import router as files_router
from app.services.cleanup import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# tells the app to serve whatever endpoints are there in files.py
# at /<endpoint>

@app.get("/health")
async def health():
    return { "status" : "ok" }

app.include_router(files_router)
app.mount("/", StaticFiles(directory="static", html=True), name="TFS")