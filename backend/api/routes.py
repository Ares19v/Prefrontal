import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import QueryRequest, ExplainResponse
from rag.retriever import Retriever
from llm.client import GeminiClient

router = APIRouter()
retriever = Retriever(top_k=5)
llm = GeminiClient()


@router.get("/health")
def health():
    return {"status": "ok", "model": "groq/llama-3.3-70b-versatile", "embedder": "BAAI/bge-base-en-v1.5"}


@router.post("/explain")
async def explain(request: QueryRequest):
    """
    SSE streaming endpoint.
    Emits: context_ready → chunks → done (or error)
    """
    async def event_stream():
        # Step 1: Retrieve relevant chunks
        retrieval = retriever.retrieve(request.query)
        context = retriever.build_context(retrieval["chunks"])
        sources = retrieval["sources"]

        # Emit retrieval metadata immediately
        yield _sse({
            "type": "context_ready",
            "sources": sources,
            "retrieval_ms": retrieval["retrieval_ms"],
            "chunks_used": retrieval["chunks_used"],
        })

        # Step 2: Stream Gemini response
        async for event in _async_stream(request.query, context, sources):
            yield _sse(event)

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


async def _async_stream(query: str, context: str, sources: list[str]):
    """Wrap the sync generator in an async one."""
    import asyncio
    loop = asyncio.get_running_loop()
    gen = llm.stream(query, context, sources)
    # The stream() method is a sync generator — iterate it
    for event in gen:
        yield event
        await asyncio.sleep(0)  # yield control back to event loop
