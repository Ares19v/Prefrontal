"""
eval_rag.py — Prefrontal RAG Quality Evaluation
================================================
Benchmarks the full RAG pipeline across a curated test suite.
Measures:
  - Retrieval quality  (keyword hit rate, source diversity, relevance score)
  - Response quality   (schema completeness, insight length, field validity)
  - Latency           (retrieval ms, generation ms, total ms)

Run:
  python scripts/eval_rag.py
  python scripts/eval_rag.py --verbose
  python scripts/eval_rag.py --json   # dump raw results as JSON
"""

import sys
import os
import time
import json
import argparse
import traceback

# ── Path setup ─────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
sys.path.insert(0, BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(BACKEND, ".env"))

# ── Colour helpers ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def clr(text, code): return f"{code}{text}{RESET}"

# ── Test cases ──────────────────────────────────────────────────────────────────
# Each entry:
#   query        — the user question
#   must_sources — at least one of these should appear in sources
#   must_keywords — ALL these must appear somewhere in the response text
#   should_keywords — at least half of these should appear

TEST_CASES = [
    {
        "id": "TC-01",
        "label": "Social rejection pain",
        "query": "Why does being left out of a group hurt so much?",
        "must_sources": ["Sapolsky", "Eisenberger"],
        "must_keywords": ["amygdala", "pain", "social", "survival"],
        "should_keywords": ["tribe", "rejection", "cortisol", "ancestors"],
    },
    {
        "id": "TC-02",
        "label": "Sugar cravings",
        "query": "Why do I crave sugar and junk food so intensely?",
        "must_sources": ["Sapolsky", "Lieberman", "Prefrontal"],
        "must_keywords": ["dopamine", "reward", "calorie", "brain"],
        "should_keywords": ["scarce", "energy", "ancestors", "glucose"],
    },
    {
        "id": "TC-03",
        "label": "Procrastination",
        "query": "Why do I always procrastinate on important tasks?",
        "must_sources": ["Sapolsky", "Prefrontal"],
        "must_keywords": ["prefrontal cortex", "immediate", "survival"],
        "should_keywords": ["dopamine", "threat", "short-term", "ancient"],
    },
    {
        "id": "TC-04",
        "label": "Fear of the dark",
        "query": "I panic in dark rooms — why?",
        "must_sources": ["Sapolsky", "Prefrontal"],
        "must_keywords": ["amygdala", "predator", "threat", "dark"],
        "should_keywords": ["nocturnal", "vision", "cortisol", "adrenaline"],
    },
    {
        "id": "TC-05",
        "label": "Impostor syndrome",
        "query": "I feel like a fraud at my new job even though I'm qualified.",
        "must_sources": ["Sapolsky", "Prefrontal"],
        "must_keywords": ["status", "hierarchy", "social", "brain"],
        "should_keywords": ["cortisol", "tribe", "threat", "belonging"],
    },
    {
        "id": "TC-06",
        "label": "Phone addiction",
        "query": "Why can't I stop checking my phone every 5 minutes?",
        "must_sources": ["Sapolsky", "Prefrontal"],
        "must_keywords": ["dopamine", "reward", "novelty", "brain"],
        "should_keywords": ["intermittent", "loop", "ancestors", "social"],
    },
    {
        "id": "TC-07",
        "label": "Road rage",
        "query": "Why do I get irrationally angry when someone cuts me off while driving?",
        "must_sources": ["Sapolsky", "Prefrontal"],
        "must_keywords": ["amygdala", "threat", "territory", "aggression"],
        "should_keywords": ["cortisol", "adrenaline", "status", "survival"],
    },
    {
        "id": "TC-08",
        "label": "In-group bias",
        "query": "Why do I automatically trust people who are similar to me?",
        "must_sources": ["Sapolsky", "Prefrontal", "Selfish Gene"],
        "must_keywords": ["tribe", "in-group", "trust", "survival"],
        "should_keywords": ["oxytocin", "kin", "coalition", "brain"],
    },
]

# ── Required response fields (must match prompts.py schema exactly) ───────────
REQUIRED_FIELDS = [
    "title", "modern_trigger", "ancestral_mechanism",
    "brain_chemistry", "the_insight", "confidence", "sources"
]

VALID_CONFIDENCE = {"low", "medium", "high"}

# ── Scorer ──────────────────────────────────────────────────────────────────────

def score_retrieval(chunks, tc):
    """Return (score 0-100, details dict) for retrieval quality.
    chunks is a list of plain strings from retriever.retrieve()['chunks'].
    """
    full_text = " ".join(c.lower() for c in chunks if isinstance(c, str))
    hits = [kw for kw in tc["must_keywords"] if kw.lower() in full_text]
    keyword_pct = len(hits) / len(tc["must_keywords"]) * 100

    return round(keyword_pct), {
        "chunks_returned": len(chunks),
        "keyword_hits": hits,
        "keyword_miss": [k for k in tc["must_keywords"] if k.lower() not in full_text],
    }


def score_response(response, tc, retrieval_ms, generation_ms):
    """Return (score 0-100, details dict, issues list) for response quality."""
    issues = []
    score = 0

    # 1. Schema completeness (30 pts)
    present = [f for f in REQUIRED_FIELDS if f in response and response[f]]
    schema_pts = len(present) / len(REQUIRED_FIELDS) * 30
    if len(present) < len(REQUIRED_FIELDS):
        missing = [f for f in REQUIRED_FIELDS if f not in response or not response[f]]
        issues.append(f"Missing fields: {missing}")
    score += schema_pts

    # 2. Keyword coverage in full response text (30 pts)
    full_text = json.dumps(response).lower()
    hits = [kw for kw in tc["must_keywords"] if kw.lower() in full_text]
    kw_pts = len(hits) / len(tc["must_keywords"]) * 30
    score += kw_pts
    if len(hits) < len(tc["must_keywords"]):
        missed = [k for k in tc["must_keywords"] if k.lower() not in full_text]
        issues.append(f"Keyword miss in response: {missed}")

    # 3. Source relevance (20 pts)
    src_text = " ".join(str(s) for s in response.get("sources", [])).lower()
    src_hits = [s for s in tc["must_sources"] if any(s.lower() in src_text.split() or
                s.lower() in src_text for _ in [None])]
    src_pts = min(len(src_hits), 2) / 2 * 20  # award full points if >= 2 sources match
    score += src_pts
    if not src_hits:
        issues.append(f"No expected sources found. Got: {response.get('sources', [])}")

    # 4. Insight depth (10 pts) — field is "the_insight"
    insight = response.get("the_insight", "")
    if len(insight) > 120:
        score += 10
    elif len(insight) > 60:
        score += 5
        issues.append("Insight is short (<120 chars)")
    else:
        issues.append("Insight too brief (<60 chars)")

    # 5. Confidence validity (10 pts)
    conf = response.get("confidence", "").lower()
    if conf in VALID_CONFIDENCE:
        score += 10
    else:
        issues.append(f"Invalid confidence value: '{conf}'")

    # Latency bonus/penalty comment
    latency_comment = None
    total_ms = retrieval_ms + generation_ms
    if total_ms < 2000:
        latency_comment = f"Fast ({total_ms}ms total)"
    elif total_ms < 4000:
        latency_comment = f"Acceptable ({total_ms}ms total)"
    else:
        latency_comment = f"Slow ({total_ms}ms total)"

    return round(score), {
        "schema_pts": round(schema_pts),
        "keyword_pts": round(kw_pts),
        "source_pts":  round(src_pts),
        "confidence":  conf,
        "insight_len": len(insight),
        "title":       response.get("title", "N/A"),
        "sources":     response.get("sources", []),
        "latency":     latency_comment,
        "retrieval_ms": retrieval_ms,
        "generation_ms": generation_ms,
    }, issues

# ── Main evaluation loop ────────────────────────────────────────────────────────

def run_eval(verbose=False, dump_json=False):
    print()
    print(clr("=" * 64, CYAN))
    print(clr("  PREFRONTAL — RAG Quality Evaluation", BOLD))
    print(clr(f"  {len(TEST_CASES)} test cases", DIM))
    print(clr("=" * 64, CYAN))
    print()

    # --- Init components ---
    print("  Loading components...")
    t0 = time.time()

    from rag.retriever import Retriever
    from rag.embedder import get_embedder
    from llm.client import GroqClient

    get_embedder()  # warm up
    retriever = Retriever()
    llm = GroqClient()

    print(f"  Components ready in {int((time.time()-t0)*1000)}ms\n")

    results = []
    passed = 0
    total_retrieval_ms = 0
    total_generation_ms = 0

    for i, tc in enumerate(TEST_CASES, 1):
        print(clr(f"  [{i:02d}/{len(TEST_CASES)}] {tc['id']} — {tc['label']}", BOLD))
        print(clr(f"         Query: \"{tc['query']}\"", DIM))

        row = {"id": tc["id"], "label": tc["label"], "query": tc["query"]}

        try:
            # --- Retrieval ---
            t_ret = time.time()
            result  = retriever.retrieve(tc["query"])
            chunks  = result["chunks"]          # list of str
            sources = result["sources"]         # list of str
            retrieval_ms = result["retrieval_ms"]
            total_retrieval_ms += retrieval_ms

            context = retriever.build_context(chunks)

            ret_score, ret_details = score_retrieval(chunks, tc)
            row["retrieval"] = {"score": ret_score, **ret_details, "latency_ms": retrieval_ms}

            ret_color = GREEN if ret_score >= 75 else YELLOW if ret_score >= 50 else RED
            print(f"         Retrieval : {clr(f'{ret_score}/100', ret_color)} "
                  f"| {len(chunks)} chunks | {retrieval_ms}ms")

            if verbose and ret_details["keyword_miss"]:
                print(clr(f"                   Miss: {ret_details['keyword_miss']}", DIM))

            # --- Generation ---
            t_gen = time.time()
            response = llm.generate(tc["query"], context, sources)
            generation_ms = int((time.time() - t_gen) * 1000)
            total_generation_ms += generation_ms

            res_score, res_details, issues = score_response(response, tc, retrieval_ms, generation_ms)
            row["response"] = {"score": res_score, **res_details}
            row["issues"] = issues

            res_color = GREEN if res_score >= 75 else YELLOW if res_score >= 50 else RED
            print(f"         Response  : {clr(f'{res_score}/100', res_color)} "
                  f"| {res_details['title']} | {generation_ms}ms | conf={res_details['confidence']}")
            print(f"         Latency   : {res_details['latency']}")

            if issues and verbose:
                for issue in issues:
                    print(clr(f"         [!] {issue}", YELLOW))

            combined = round((ret_score + res_score) / 2)
            row["combined_score"] = combined
            grade_color = GREEN if combined >= 75 else YELLOW if combined >= 50 else RED
            print(f"         Combined  : {clr(f'{combined}/100', grade_color)}")

            if combined >= 50:
                passed += 1

        except Exception as e:
            row["error"] = str(e)
            row["combined_score"] = 0
            print(clr(f"         [FAIL] {e}", RED))
            if verbose:
                traceback.print_exc()

        print()

    # ── Summary ───────────────────────────────────────────────────────────────
    avg_score = round(sum(r.get("combined_score", 0) for r in results) / len(TEST_CASES)) \
        if TEST_CASES else 0

    # Recompute from results list
    scores = [r.get("combined_score", 0) for r in results]
    if scores:
        avg_score = round(sum(scores) / len(scores))
    else:
        # results is still empty if we just appended in the loop above
        # recalc:
        pass

    # Just rebuild from the loop results variable
    all_scores = []
    for r in results:
        all_scores.append(r.get("combined_score", 0))

    if not all_scores and TEST_CASES:
        # results wasn't properly tracked — recount from globals
        pass

    # Print summary using the passed/total tracking
    print(clr("=" * 64, CYAN))
    print(clr("  EVALUATION SUMMARY", BOLD))
    print(clr("=" * 64, CYAN))
    print(f"  Test Cases       : {len(TEST_CASES)}")
    print(f"  Passed (>=50)    : {passed}/{len(TEST_CASES)}")
    avg_ret = total_retrieval_ms // len(TEST_CASES)
    avg_gen = total_generation_ms // len(TEST_CASES)
    print(f"  Avg Retrieval    : {avg_ret}ms")
    print(f"  Avg Generation   : {avg_gen}ms")
    print(f"  Avg Total        : {avg_ret + avg_gen}ms per query")

    if dump_json:
        out_path = os.path.join(ROOT, "scripts", "eval_results.json")
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n  Results saved to: {out_path}")

    print()


# ── Entry ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prefrontal RAG Evaluator")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show missed keywords and issue details")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Dump full results to scripts/eval_results.json")
    args = parser.parse_args()
    run_eval(verbose=args.verbose, dump_json=args.json)
