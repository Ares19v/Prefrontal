import os, sys, time, json, urllib.request, requests

QUERIES = [
    ("Public Speaking Fear", "Why am I terrified of public speaking in front of large crowds?"),
    ("Digital Doomscrolling", "Why can't I stop doomscrolling on social media late at night?"),
    ("Imposter Syndrome", "Why do I constantly feel like an intellectual fraud in meetings?"),
    ("Sugar/Fat Cravings", "Why do I crave sugary, calorie-dense foods when I am stressed?"),
    ("Rejection Sensitivity", "Why does being ghosted or socially rejected feel like physical pain?"),
    ("Procrastination", "Why do I delay working on my most important long-term goals for quick dopamine?"),
    ("Loss Aversion", "Why does losing $100 feel twice as painful as gaining $100 feels good?"),
    ("Status Seeking", "Why do people buy luxury brands and expensive watches they cannot afford?"),
    ("Tribal Polarization", "Why do people become intensely hostile toward opposing political groups?"),
    ("Nighttime Anxiety", "Why do my thoughts spiral with worst-case scenarios when trying to sleep?"),
    ("Sunk Cost Fallacy", "Why do I stay in dead-end projects or relationships even when knowing they fail?"),
    ("Negativity Bias", "Why do I remember a single insult more vividly than ten compliments?"),
    ("Social FOMO", "Why do I get anxious seeing friends hanging out without me on Instagram?"),
    ("Gossip Addiction", "Why is talking about other people's social drama so universally compelling?"),
    ("In-group Favoritism", "Why are humans naturally biased toward helping family over strangers?"),
    ("Stranger Wariness", "Why do people instinctively feel cautious around unfamiliar outsiders?"),
    ("Morning Grogginess", "Why is waking up to an alarm clock so difficult even after 8 hours of sleep?"),
    ("Conflict Hyper-vigilance", "Why does my heart race for hours after a minor disagreement at work?"),
    ("Public Altruism", "Why do people feel compelled to perform charitable acts publicly?"),
    ("Peer Envy", "Why does a close friend's sudden success secretly sting even when I care about them?")
]

print("=" * 115)
print("               PREFRONTAL EVOLUTIONARY RAG PIPELINE — 20 QUERY STRESS TEST")
print("=" * 115)

results = []
total_start = time.perf_counter()

for i, (category, query) in enumerate(QUERIES, 1):
    t0 = time.perf_counter()
    retrieval_meta = {}
    explanation = {}
    err = None
    
    try:
        res = requests.post(
            "http://localhost:8000/api/explain",
            json={"query": query},
            stream=True,
            timeout=45
        )
        for line in res.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith("data: "):
                    payload = decoded[6:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        event = json.loads(payload)
                        if event.get("type") == "context_ready":
                            retrieval_meta = event
                        elif event.get("type") == "done":
                            explanation = event.get("explanation", {})
                        elif event.get("type") == "error":
                            err = event.get("message")
                    except Exception:
                        pass
    except Exception as e:
        err = str(e)

    total_lat = (time.perf_counter() - t0) * 1000
    retrieval_ms = retrieval_meta.get("retrieval_ms", 0)
    sources = retrieval_meta.get("sources", [])
    
    has_content = bool(explanation.get("ancestral_mechanism") or explanation.get("title") or explanation.get("the_insight") or explanation.get("brain_chemistry"))
    status = "PASS" if (has_content and not err) else ("FAIL: " + str(err) if err else "FAIL (empty)")

    results.append({
        "id": i,
        "category": category,
        "query": query,
        "retrieval_ms": retrieval_ms,
        "total_lat": round(total_lat, 1),
        "sources_count": len(sources),
        "sources_str": ", ".join(sources[:2]) if sources else "None",
        "explanation": explanation,
        "headline": explanation.get("title") or explanation.get("ancestral_mechanism") or "Evolutionary Mismatch",
        "status": status
    })
    
    print(f"[{i:02d}/20] {category:<24} | Status: {status[:15]:<10} | RAG: {retrieval_ms:>4}ms | Total: {total_lat:>6.1f}ms | Sources: {len(sources)}", flush=True)


print("\n" + "=" * 115)
print("ID  | Category               | Retrieval | Total Lat | Sources | Evolutionary Thesis")
print("-" * 115)

for r in results:
    headline_preview = (r["headline"][:36] + '...') if len(r["headline"]) > 39 else r["headline"]
    print(f"{r['id']:<3d} | {r['category']:<24} | {r['retrieval_ms']:>5}ms   | {r['total_lat']:>6.1f}ms | {r['sources_count']:>4}    | {headline_preview}")

print("=" * 115)
pass_count = sum(1 for r in results if "PASS" in r["status"])
avg_retrieval = sum(r["retrieval_ms"] for r in results) / len(results) if results else 0
avg_total = sum(r["total_lat"] for r in results) / len(results) if results else 0
total_time = time.perf_counter() - total_start

print("\n[GLOBAL EVALUATION REPORT]")
print(f"[*] Total Queries Evaluated   : {len(results)}/20")
print(f"[*] Success Rate              : {(pass_count / len(results)) * 100:.1f}% ({pass_count}/{len(results)} queries passed)")
print(f"[*] Avg BGE-Base Retrieval    : {avg_retrieval:.1f} ms")
print(f"[*] Avg End-to-End LLM Latency: {avg_total:.1f} ms")
print(f"[*] Total Test Suite Duration : {total_time:.2f}s")
print("=" * 115)

with open('test_results_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
print("[*] Full structured JSON results saved to test_results_detailed.json")
