"""
test_all.py — Prefrontal System Integration Test Suite
========================================================
Runs a comprehensive check on every layer of the project:

  [1]  Environment (.env variables loaded)
  [2]  Pinecone connection & index health
  [3]  Embedding model (BGE) — load + 768-dim output
  [4]  Retriever — semantic search returns results
  [5]  Gemini LLM — generates a valid response
  [6]  Full RAG pipeline — end-to-end explain flow
  [7]  Seed JSON — schema validation for all 50 entries
  [8]  Backend API — /health and /explain HTTP endpoints

Usage:
    cd c:\\Users\\Devansh Tyagi\\Desktop\\Projects\\Prefrontal
    .\\backend\\venv\\Scripts\\activate
    python scripts/test_all.py

    # To test the API endpoints, make sure the backend is running first:
    # uvicorn main:app --port 8000  (from backend/ dir)
"""

import os
import sys
import json
import time
import traceback

# ── Path setup so we can import backend modules ──────────────────────────────
ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
SEED_PATH   = os.path.join(ROOT_DIR, "knowledge_base", "curated", "seed.json")

sys.path.insert(0, BACKEND_DIR)

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(BACKEND_DIR, ".env"))

# ── Terminal colors (works on Windows with PYTHONUTF8=1) ─────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS = f"{GREEN}[PASS]{RESET}"
FAIL = f"{RED}[FAIL]{RESET}"
WARN = f"{YELLOW}[WARN]{RESET}"
INFO = f"{CYAN}[INFO]{RESET}"

results = []

def section(title: str):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def ok(label: str, detail: str = ""):
    msg = f"  {PASS}  {label}"
    if detail:
        msg += f"  {CYAN}({detail}){RESET}"
    print(msg)
    results.append(("pass", label))


def fail(label: str, err: str = ""):
    msg = f"  {FAIL}  {label}"
    if err:
        msg += f"\n         {RED}{err}{RESET}"
    print(msg)
    results.append(("fail", label))


def warn(label: str, detail: str = ""):
    msg = f"  {WARN}  {label}"
    if detail:
        msg += f"  {YELLOW}({detail}){RESET}"
    print(msg)
    results.append(("warn", label))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1 — Environment Variables
# ─────────────────────────────────────────────────────────────────────────────
section("TEST 1 — Environment Variables")

required_vars = {
    "GROQ_API_KEY":        "gsk_",           # Groq key prefix
    "PINECONE_API_KEY":    "pcsk_",
    "PINECONE_INDEX_NAME": "prefrontal",
}

for var, expected_prefix in required_vars.items():
    value = os.getenv(var, "")
    if not value:
        fail(f"{var} is set", "MISSING — check backend/.env")
    elif not value.startswith(expected_prefix):
        fail(f"{var} looks valid", f"Expected prefix '{expected_prefix}', got '{value[:8]}...'")
    else:
        ok(f"{var} is set and looks valid", f"{value[:12]}...")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 — Pinecone Connection & Index
# ─────────────────────────────────────────────────────────────────────────────
section("TEST 2 — Pinecone Connection & Index")

pinecone_index = None
try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    ok("Pinecone client initialised")

    index_name = os.getenv("PINECONE_INDEX_NAME")
    pinecone_index = pc.Index(index_name)
    stats = pinecone_index.describe_index_stats()
    ok(f"Connected to index '{index_name}'")

    total = stats.total_vector_count
    dim   = stats.dimension
    if total == 0:
        fail("Index has vectors", "Index is empty — run build_index.py first")
    elif total < 50:
        warn("Index vector count", f"Only {total} vectors — seed may be partially ingested")
    else:
        ok(f"Index contains vectors", f"{total} vectors, {dim}-dim")

    if dim != 768:
        fail(f"Index dimension is 768", f"Got {dim} — mismatch with BGE model")
    else:
        ok("Index dimension is 768", "matches BAAI/bge-base-en-v1.5")

except Exception as e:
    fail("Pinecone connection", str(e))
    traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3 — Embedding Model (BGE)
# ─────────────────────────────────────────────────────────────────────────────
section("TEST 3 — Embedding Model (BAAI/bge-base-en-v1.5)")

embedder = None
try:
    t0 = time.time()
    from rag.embedder import get_embedder
    embedder = get_embedder()
    load_ms = int((time.time() - t0) * 1000)
    ok("BGE embedder loaded", f"{load_ms}ms")

    test_text = "fear of being alone"
    t0 = time.time()
    vector = embedder.embed_query(test_text)
    embed_ms = int((time.time() - t0) * 1000)

    if len(vector) != 768:
        fail(f"Output dimension is 768", f"Got {len(vector)}")
    else:
        ok("embed_query() returns 768-dim vector", f"{embed_ms}ms")

    magnitude = sum(v**2 for v in vector) ** 0.5
    if abs(magnitude - 1.0) > 0.01:
        warn("Vector is normalized", f"magnitude = {magnitude:.4f}")
    else:
        ok("Vector is L2-normalized", f"magnitude = {magnitude:.4f}")

except Exception as e:
    fail("Embedding model", str(e))
    traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4 — Retriever (Semantic Search)
# ─────────────────────────────────────────────────────────────────────────────
section("TEST 4 — Retriever (Pinecone Semantic Search)")

try:
    from rag.retriever import Retriever
    retriever = Retriever(top_k=5)

    t0 = time.time()
    result = retriever.retrieve("I feel anxious when I get no likes on social media")
    retrieval_ms = result["retrieval_ms"]

    chunks = result["chunks"]
    sources = result["sources"]

    if not chunks:
        fail("Retriever returned chunks", "Got 0 — index may be empty")
    else:
        ok(f"Retriever returned {len(chunks)} chunks", f"{retrieval_ms}ms")

    if not sources:
        warn("Sources returned", "No source metadata found in results")
    else:
        ok(f"Sources returned", f"{', '.join(sources[:3])}")

    # Relevance sanity check
    combined = " ".join(chunks).lower()
    keywords = ["social", "tribe", "rejection", "brain", "survival", "dopamine"]
    found = [k for k in keywords if k in combined]
    if len(found) >= 2:
        ok(f"Retrieved content is relevant", f"Found keywords: {', '.join(found)}")
    else:
        warn("Retrieved content relevance", f"Only found: {found}")

    context = retriever.build_context(chunks)
    if len(context) > 100:
        ok("build_context() assembles context block", f"{len(context)} chars")
    else:
        fail("build_context() assembles context block", "Too short")

except Exception as e:
    fail("Retriever", str(e))
    traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5 — Gemini LLM Client
# ─────────────────────────────────────────────────────────────────────────────
section("TEST 5 — Gemini LLM Client (generate)")

gemini_client = None
try:
    from llm.client import GeminiClient
    gemini_client = GeminiClient()
    ok("GeminiClient initialised")

    # Small context to save tokens
    mini_context = (
        "Social rejection triggers the anterior cingulate cortex, "
        "the same region that processes physical pain. "
        "This is because tribal exclusion was lethal for early humans."
    )
    mini_query = "Why does being ignored on social media hurt?"
    mini_sources = ["Behave — Sapolsky", "Eisenberger et al. 2003"]

    t0 = time.time()
    response = gemini_client.generate(mini_query, mini_context, mini_sources)
    gen_ms = int((time.time() - t0) * 1000)
    ok("generate() completed without error", f"{gen_ms}ms")

    required_fields = ["title", "modern_trigger", "ancestral_mechanism",
                       "brain_chemistry", "the_insight", "confidence", "sources"]
    missing = [f for f in required_fields if f not in response]
    if missing:
        fail(f"Response has all required fields", f"Missing: {missing}")
    else:
        ok("Response JSON has all 7 required fields")

    if response.get("confidence") not in ("high", "medium", "low"):
        warn("Confidence field valid value", f"Got: '{response.get('confidence')}'")
    else:
        ok(f"Confidence field is valid", response.get("confidence"))

    title = response.get("title", "")
    if len(title) > 50:
        warn("Title is concise", f"Title is {len(title)} chars — may be too long")
    else:
        ok("Title is concise", f'"{title}"')

except Exception as e:
    err_str = str(e)
    if "429" in err_str or "quota" in err_str.lower() or "ResourceExhausted" in err_str:
        warn("Gemini LLM client", "Rate-limited (429) — API key is valid but hit per-minute quota. Wait 60s and retry.")
        results.pop()  # remove the auto-added fail
        results.append(("warn", "Gemini LLM client (rate limited)"))
    else:
        fail("Gemini LLM client", err_str[:200])
        traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6 — Full RAG Pipeline (End-to-End)
# ─────────────────────────────────────────────────────────────────────────────
section("TEST 6 — Full RAG Pipeline (End-to-End)")

try:
    if retriever and gemini_client:
        query = "Why do I procrastinate on important tasks?"
        print(f"  {INFO}  Query: \"{query}\"")

        t0 = time.time()
        retrieval = retriever.retrieve(query)
        context   = retriever.build_context(retrieval["chunks"])
        sources   = retrieval["sources"]
        response  = gemini_client.generate(query, context, sources)
        total_ms  = int((time.time() - t0) * 1000)

        ok("End-to-end pipeline completed", f"{total_ms}ms total")

        insight = response.get("the_insight", "")
        if len(insight) > 50:
            ok("Insight section is meaningful", f'"{insight[:80]}..."')
        else:
            warn("Insight section", "Short — may need prompt tuning")

        sources_in_response = response.get("sources", [])
        if sources_in_response:
            ok("Sources populated in response", ", ".join(sources_in_response[:2]))
        else:
            warn("Sources in response", "Empty — check source metadata in index")
    else:
        warn("Full RAG pipeline", "Skipped — Retriever or GeminiClient not available")

except Exception as e:
    err_str = str(e)
    if "429" in err_str or "quota" in err_str.lower() or "ResourceExhausted" in err_str:
        warn("Full RAG pipeline", "Rate-limited (429) — skipped, not a failure.")
    else:
        fail("Full RAG pipeline", err_str[:200])
        traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7 — Seed JSON Schema Validation
# ─────────────────────────────────────────────────────────────────────────────
section("TEST 7 — Seed JSON Schema Validation")

try:
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        seed_data = json.load(f)

    ok(f"seed.json loaded successfully", f"{len(seed_data)} entries")

    REQUIRED_FIELDS = ["id", "behavior", "modern_trigger", "ancestral_mechanism",
                       "brain_region", "brain_chemistry", "the_insight", "tags", "sources"]

    invalid_entries = []
    for i, entry in enumerate(seed_data):
        missing = [f for f in REQUIRED_FIELDS if f not in entry]
        if missing:
            invalid_entries.append((i, entry.get("id", f"entry_{i}"), missing))

    if invalid_entries:
        for i, eid, missing in invalid_entries:
            fail(f"Entry {i} '{eid}' valid schema", f"Missing: {missing}")
    else:
        ok(f"All {len(seed_data)} entries have required schema fields")

    # Check IDs are unique
    ids = [e.get("id") for e in seed_data]
    unique_ids = set(ids)
    if len(unique_ids) < len(ids):
        dupes = [id for id in ids if ids.count(id) > 1]
        fail("All entry IDs are unique", f"Duplicates: {list(set(dupes))}")
    else:
        ok("All entry IDs are unique")

    # Count entries
    if len(seed_data) >= 50:
        ok(f"Seed has 50 entries", f"Found {len(seed_data)}")
    else:
        warn(f"Seed has 50 entries", f"Only {len(seed_data)} — may want to add more")

except FileNotFoundError:
    fail("seed.json exists", f"Not found at {SEED_PATH}")
except json.JSONDecodeError as e:
    fail("seed.json is valid JSON", str(e))
except Exception as e:
    fail("seed.json validation", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8 — Backend HTTP API (requires server running)
# ─────────────────────────────────────────────────────────────────────────────
section("TEST 8 — Backend HTTP API (http://localhost:8000)")

try:
    import urllib.request
    import urllib.error

    # 8a: Health check
    try:
        req = urllib.request.urlopen("http://localhost:8000/api/health", timeout=5)
        body = json.loads(req.read().decode())
        if body.get("status") == "ok" and ("groq" in body.get("model", "") or "gemini" in body.get("model", "")):
            ok("GET /api/health returns 200 OK", f"model={body.get('model')}")
        else:
            warn("GET /api/health", f"Unexpected body: {body}")
    except urllib.error.URLError:
        warn("GET /api/health", "Backend not running — start with 'uvicorn main:app --port 8000' in backend/")

    # 8b: Explain endpoint (SSE)
    try:
        payload = json.dumps({"query": "Why do I fear public speaking?"}).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:8000/api/explain",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=30)
        
        full_body = resp.read().decode("utf-8")
        events = [line for line in full_body.split("\n") if line.startswith("data: ")]
        
        if not events:
            fail("POST /api/explain returns SSE events", "No data: events found")
        else:
            # Find 'done' event
            done_event = None
            for ev in events:
                data_str = ev[6:]  # strip "data: "
                if data_str == "[DONE]":
                    continue
                try:
                    parsed = json.loads(data_str)
                    if parsed.get("type") == "done":
                        done_event = parsed
                        break
                except json.JSONDecodeError:
                    pass

            if done_event:
                explanation = done_event.get("explanation", {})
                ok("POST /api/explain — 'done' event received")
                ok("Response has 'explanation' payload", f"title: '{explanation.get('title', 'N/A')[:50]}'")
            else:
                # At minimum we got events
                event_types = []
                for ev in events:
                    try:
                        parsed = json.loads(ev[6:])
                        event_types.append(parsed.get("type"))
                    except Exception:
                        pass
                warn("POST /api/explain — 'done' event", f"Got events: {event_types}")

    except urllib.error.URLError:
        warn("POST /api/explain", "Backend not running — start it first")
    except Exception as e:
        fail("POST /api/explain", str(e))

except Exception as e:
    fail("HTTP API tests", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
section("TEST SUMMARY")

passed  = sum(1 for r in results if r[0] == "pass")
failed  = sum(1 for r in results if r[0] == "fail")
warned  = sum(1 for r in results if r[0] == "warn")
total   = len(results)

print(f"\n  {GREEN}PASSED : {passed}/{total}{RESET}")
if warned:
    print(f"  {YELLOW}WARNED : {warned}/{total}{RESET}")
if failed:
    print(f"  {RED}FAILED : {failed}/{total}{RESET}")
    print(f"\n  {RED}Failed checks:{RESET}")
    for r in results:
        if r[0] == "fail":
            print(f"    {RED}x{RESET}  {r[1]}")

print()

if failed == 0:
    print(f"  {GREEN}{BOLD}All systems operational. Prefrontal is ready.{RESET}\n")
elif failed <= 2:
    print(f"  {YELLOW}{BOLD}Minor issues — check warnings above.{RESET}\n")
else:
    print(f"  {RED}{BOLD}Critical failures detected — review above.{RESET}\n")

sys.exit(0 if failed == 0 else 1)
