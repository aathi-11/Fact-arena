"""
Fact-Arena CLI & Algorithmic Analysis Utility
=============================================
Provides command-line fact-checking, PEAS formulation display,
and hybrid search (BM25 + FAISS + RRF) algorithmic benchmarking.
"""

import sys
import os
import json
import time
import argparse
from typing import List, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.graph.debate_graph import run_debate
from src.retrieval.hybrid_search import (
    bm25_search,
    dense_search,
    reciprocal_rank_fusion,
    hybrid_search,
    build_faiss_index
)


def print_header(title: str):
    print("\n" + "=" * 75)
    print(f"  {title}")
    print("=" * 75)


def display_peas_formulation():
    """Prints the formal PEAS and Environment Analysis (Rubrics 1 & 2)."""
    print_header("PEAS FORMULATION (RUSSELL & NORVIG TAXONOMY)")
    print("""
+-----------------------+------------------------------------------+------------------------------+----------------------------------+------------------------------------+
| Agent Component       | Performance Measure (P)                  | Environment (E)              | Actuators (A)                    | Sensors (S)                        |
+-----------------------+------------------------------------------+------------------------------+----------------------------------+------------------------------------+
| Claim Normalizer      | Atomicity, sub-claim precision           | Unstructured text space      | Decomposed JSON sub-claims       | Raw user claim string              |
| Pro & Con Debaters    | Grounding accuracy, retrieval relevance  | Live Web (Tavily, DDGS)      | Stance-biased queries, [Ex] tags | Web results, prior turns           |
| Citation Guardrail    | 100% hallucination detection, 0% false + | Evidence pool registry       | Audit flags, warning notices     | Regex cited IDs [Ex], pool keys    |
| Supreme Judge         | Calibration, epistemic nuance, accuracy  | Full transcript & audit logs | Verdict, confidence %, rationale | Complete state graph history       |
+-----------------------+------------------------------------------+------------------------------+----------------------------------+------------------------------------+
    """)

    print_header("ENVIRONMENT PROPERTIES (7 CANONICAL DIMENSIONS)")
    print("""
  1. Observability   : Partially Observable (agents retrieve top-k subsets of web knowledge)
  2. Agents          : Multi-Agent (Adversarial Pro/Con + Collaborative Normalizer + Impartial Judge)
  3. Determinism     : Stochastic (Web retrieval variance + temperature-conditioned LLM sampling)
  4. Episodic/Seq    : Sequential (Multi-round debate where each argument directly counters prior turns)
  5. Static/Dynamic  : Dynamic (Real-time live web environment continuously evolving)
  6. Discrete/Cont   : Discrete (Discrete tokens, debate turns, rounds, and categorical verdicts)
  7. Transition Model: Unknown (Requires active web search & retrieval rather than closed-world model)
    """)


def run_search_benchmark():
    """Runs an algorithmic benchmark comparing BM25 vs FAISS Dense vs Hybrid RRF (Rubric 3)."""
    print_header("ALGORITHMIC SEARCH BENCHMARK: BM25 vs FAISS DENSE vs HYBRID RRF")

    corpus = [
        "Cardiovascular exercise and running significantly improve heart muscle endurance and reduce arterial plaque.",
        "High blood pressure and hypertension are major risk factors for sudden cardiac arrest and stroke.",
        "Clinical trials show moderate caffeine intake has neutral to slight protective effects on cardiovascular mortality.",
        "Excessive caffeine intake above 400mg per day may induce palpitations, cardiac arrhythmias, and acute anxiety.",
        "The Great Wall of China is built from stone, tamped earth, and bricks along the northern borders.",
        "Satellite imagery confirms low Earth orbit astronauts cannot discern the Great Wall without optical zoom lenses.",
        "Sedentary lifestyles correlate with higher rates of metabolic syndrome, diabetes, and coronary artery disease.",
        "Randomized controlled trials confirm daily 30-minute moderate aerobic activity reduces all-cause mortality."
    ]

    test_query = "exercise and cardiovascular disease risk reduction"
    print(f"Test Query: \"{test_query}\"")
    print(f"Corpus Size: {len(corpus)} documents\n")

    # 1. BM25
    t0 = time.perf_counter()
    bm25_indices = bm25_search(test_query, corpus, k=3)
    bm25_time = (time.perf_counter() - t0) * 1000

    # 2. FAISS Dense
    t0 = time.perf_counter()
    index, _ = build_faiss_index(corpus)
    dense_indices = dense_search(test_query, index, k=3)
    dense_time = (time.perf_counter() - t0) * 1000

    # 3. Hybrid RRF
    t0 = time.perf_counter()
    fused_indices = reciprocal_rank_fusion(dense_indices, bm25_indices, c=60)
    hybrid_time = (time.perf_counter() - t0) * 1000

    print("--- [1] BM25 Okapi (Sparse Lexical) ---")
    for rank, idx in enumerate(bm25_indices, 1):
        print(f"  Rank {rank} (Doc #{idx}): {corpus[idx][:75]}...")
    print(f"  Latency: {bm25_time:.2f} ms\n")

    print("--- [2] FAISS IndexFlatIP (Dense Semantic) ---")
    for rank, idx in enumerate(dense_indices, 1):
        print(f"  Rank {rank} (Doc #{idx}): {corpus[idx][:75]}...")
    print(f"  Latency: {dense_time:.2f} ms\n")

    print("--- [3] Hybrid Reciprocal Rank Fusion (RRF: c=60) ---")
    for rank, idx in enumerate(fused_indices[:3], 1):
        print(f"  Rank {rank} (Doc #{idx}): {corpus[idx][:75]}...")
    print(f"  Latency: {hybrid_time:.2f} ms\n")

    overlap = len(set(bm25_indices).intersection(set(dense_indices)))
    print(f"Top-3 Overlap between Sparse and Dense: {overlap}/3 items.")
    print("Hybrid RRF harmonizes exact keyword matching with deep semantic vector similarity.")


def run_fact_check(claim: str, rounds: int = 1, export_file: str = None):
    """Executes full multi-agent fact check for a given claim."""
    print_header(f"VERITAS FACT CHECK: \"{claim}\"")
    print(f"Debate Rounds Configured: {rounds}")
    print("Executing LangGraph Multi-Agent State Machine...")

    t_start = time.time()
    state = run_debate(claim, max_rounds=rounds)
    elapsed = round(time.time() - t_start, 2)

    # 1. Sub-claims
    sub_claims = state.get("sub_claims", [])
    print(f"\n[1] Decomposed Sub-claims ({len(sub_claims)}):")
    for i, sc in enumerate(sub_claims, 1):
        print(f"    {i}. {sc}")

    # 2. Evidence Pool
    evidence = state.get("evidence_pool", {})
    print(f"\n[2] Retrieved Evidence Pool ({len(evidence)} sources):")
    for eid, ev in list(evidence.items())[:4]:
        print(f"    [{eid}] {ev.get('title', '')} -> {ev.get('url', '')}")
    if len(evidence) > 4:
        print(f"    ... and {len(evidence) - 4} more sources.")

    # 3. Turns Summary
    pro_turns = state.get("pro_turns", [])
    con_turns = state.get("con_turns", [])
    print(f"\n[3] Debate Rounds: {len(pro_turns)} Pro turn(s), {len(con_turns)} Con turn(s)")

    # 4. Supreme Judge Verdict
    v = state.get("verdict") or {}
    verdict = v.get("verdict", "unverifiable").upper()
    confidence = v.get("confidence", 0)
    rationale = v.get("rationale", "")
    uncertainty = v.get("uncertainty_note")
    guardrail = v.get("guardrail_report", {})

    print_header("SUPREME JUDGE CALIBRATED VERDICT")
    print(f"  VERDICT     : {verdict}")
    print(f"  CONFIDENCE  : {confidence}%")
    print(f"  GUARDRAIL   : {'CLEAN (All citations valid)' if guardrail.get('is_clean') else 'FLAGGED VIOLATION'}")
    print(f"  RATIONALE   : {rationale}")
    if uncertainty:
        print(f"  UNCERTAINTY : {uncertainty}")
    print(f"  PIPELINE TIME: {elapsed}s")

    if export_file:
        export_data = {
            "claim": claim,
            "sub_claims": sub_claims,
            "rounds": rounds,
            "verdict": v,
            "evidence_count": len(evidence),
            "latency_seconds": elapsed,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)
        print(f"\n[Export] Full report saved to: {export_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Veritas Agents - Fact-Arena CLI & Algorithmic Analysis"
    )
    parser.add_argument(
        "--claim",
        type=str,
        default="Moderate coffee consumption increases the risk of heart disease.",
        help="Claim string to verify"
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=1,
        help="Number of adversarial debate rounds (default: 1)"
    )
    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="Optional path to export JSON verdict report"
    )
    parser.add_argument(
        "--peas",
        action="store_true",
        help="Display formal PEAS and Environment Analysis specifications"
    )
    parser.add_argument(
        "--benchmark-search",
        action="store_true",
        help="Run BM25 vs FAISS vs Hybrid RRF retrieval benchmark"
    )

    args = parser.parse_args()

    if args.peas:
        display_peas_formulation()
    elif args.benchmark_search:
        run_search_benchmark()
    else:
        run_fact_check(claim=args.claim, rounds=args.rounds, export_file=args.export)


if __name__ == "__main__":
    main()
