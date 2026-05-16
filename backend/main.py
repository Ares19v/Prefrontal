from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="Prefrontal API",
    description="Evolutionary psychology explainer — trace modern fears to ancestral origins.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup():
    # Warm up the embedding model on startup so first query isn't slow
    from rag.embedder import get_embedder
    get_embedder()
    print("Prefrontal API ready.")
