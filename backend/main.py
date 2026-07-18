from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from controllers.analytics import router as analytics_router
from controllers.inventory import router as inventory_router
from controllers.pipeline import router as pipeline_router
from controllers.projects import router as projects_router
from database import dispose_engines, init_models, is_configured


@asynccontextmanager
async def lifespan(app: FastAPI):
    if is_configured():
        await init_models()
    yield
    await dispose_engines()


app = FastAPI(
    title="Reverie Backend",
    description="Upcycling AI agent pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

# Comment Out when in Prod
# Ensure the static directory exists and mount it
import os
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Comment Out when in Prod

app.include_router(analytics_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")
app.include_router(pipeline_router, prefix="/api")
app.include_router(projects_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}


@app.get("/health")
def health():
    return {"status": "reverie is live", "database_configured": is_configured()}
