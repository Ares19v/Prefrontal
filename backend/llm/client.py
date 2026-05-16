import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPT, RAG_PROMPT_TEMPLATE

load_dotenv()

_model = None


def get_model():
    global _model
    if _model is None:
        _model = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.4,
            max_tokens=1024,
        )
    return _model


def _clean_json(raw: str) -> str:
    """Strip markdown fences if the model wraps JSON in them."""
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


class GroqClient:
    def generate(self, query: str, context: str, sources: list[str]) -> dict:
        """
        Non-streaming: generate a full structured JSON explanation.
        Returns parsed dict or raises on failure.
        """
        model = get_model()
        prompt = RAG_PROMPT_TEMPLATE.format(context=context, query=query)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]

        response = model.invoke(messages)
        raw = _clean_json(response.content)

        parsed = json.loads(raw)
        if not parsed.get("sources") and sources:
            parsed["sources"] = sources

        return parsed

    def stream(self, query: str, context: str, sources: list[str]):
        """
        Sync generator — yields SSE-compatible event dicts.
        Streams tokens from Groq, then yields the final parsed JSON explanation.
        """
        model = get_model()
        prompt = RAG_PROMPT_TEMPLATE.format(context=context, query=query)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]

        full_text = ""
        for chunk in model.stream(messages):
            token = chunk.content
            if token:
                full_text += token
                yield {"type": "chunk", "content": token}

        # Parse and yield final result
        raw = _clean_json(full_text)
        try:
            parsed = json.loads(raw)
            if not parsed.get("sources") and sources:
                parsed["sources"] = sources
            yield {"type": "done", "explanation": parsed}
        except json.JSONDecodeError:
            yield {
                "type": "error",
                "message": "Failed to parse model output as JSON",
                "raw": raw[:500],
            }


# Alias so existing imports of GeminiClient still work
GeminiClient = GroqClient
