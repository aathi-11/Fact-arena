import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph.debate_graph import run_debate

def test_claims():
    claims = [
        "The Great Wall of China is visible from space with the naked eye.",
        "Regular exercise reduces the risk of cardiovascular disease.",
        "Moderate coffee consumption increases the risk of heart disease."
    ]

    for i, claim in enumerate(claims, 1):
        print(f"\n=== Testing Claim {i}: {claim} ===")
        res = run_debate(claim, max_rounds=2)
        print("Sub-claims:", res["sub_claims"])
        print("Pro turns count:", len(res["pro_turns"]))
        print("Con turns count:", len(res["con_turns"]))
        print("Evidence pool size:", len(res["evidence_pool"]))
        v = res["verdict"]
        print("Verdict:", v["verdict"])
        print("Confidence:", v["confidence"])
        print("Rationale:", v["rationale"][:120])
        print("Uncertainty Note:", v.get("uncertainty_note"))
        print("Latency log:", res["latency_log"])
        print("-" * 50)

if __name__ == "__main__":
    test_claims()
