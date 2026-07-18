from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from controllers.pipeline import router as pipeline_router
from controllers.projects import router as projects_router
from database import dispose_engines, init_models, is_configured

load_dotenv()


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

app.include_router(pipeline_router)
app.include_router(projects_router)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}


@app.get("/health")
def health():
    return {"status": "ok", "database_configured": is_configured()}
