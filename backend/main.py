from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm up the embedding model on startup so the first query isn't slow."""
    from rag.embedder import get_embedder
    get_embedder()
    print("✓ Prefrontal API ready.")
    yield
    # Shutdown logic (if needed) goes here


app = FastAPI(
    title="Prefrontal API",
    description="Evolutionary psychology explainer — trace modern fears to ancestral origins.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
)

app.include_router(router, prefix="/api")
