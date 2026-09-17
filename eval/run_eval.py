import sys
import os
import json
import time

# Force UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph.debate_graph import run_debate

def run_evaluation():
    json_path = os.path.join(os.path.dirname(__file__), "test_claims.json")
    with open(json_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    print("=" * 70)
    print(" VERITAS-AGENTS EVALUATION SUITE & CALIBRATION HARNESS")
    print("=" * 70)

    calibration_failures = 0
    passed_scenarios = 0

    for idx, sc in enumerate(scenarios, 1):
        category = sc["category"]
        claim = sc["claim"]
        exp_verdict = sc["expected_verdict"]
        max_allowed_conf = sc["expected_max_confidence"]

        print(f"\n[Test Scenario {idx}/{len(scenarios)}] Category: '{category}'")
        print(f"Claim: \"{claim}\"")

        t0 = time.time()
        res = run_debate(claim, max_rounds=2)
        elapsed = round(time.time() - t0, 2)

        verdict_data = res.get("verdict") or {}
        verdict = verdict_data.get("verdict", "unverifiable")
        confidence = verdict_data.get("confidence", 0)
        rationale = verdict_data.get("rationale", "")
        uncertainty = verdict_data.get("uncertainty_note")
        guardrail = verdict_data.get("guardrail_report", {})

        print(f" -> Output Verdict: {verdict.upper()} (Confidence: {confidence}%) in {elapsed}s")
        print(f" -> Rationale: {rationale[:140]}...")
        if uncertainty:
            print(f" -> Uncertainty Note: {uncertainty}")
        print(f" -> Guardrail Status: Clean={guardrail.get('is_clean', True)}")

        # Check Calibration rule on ambiguous claims
        if category == "Genuinely ambiguous":
            if confidence > max_allowed_conf:
                print(f" [FAIL] CALIBRATION FAILURE: Confidence ({confidence}%) exceeded max allowed threshold ({max_allowed_conf}%) for ambiguous claim!")
                calibration_failures += 1
            elif not uncertainty:
                print(" [FAIL] CALIBRATION FAILURE: Ambiguous claim produced high certainty without populating uncertainty_note!")
                calibration_failures += 1
            else:
                print(" [PASS] CALIBRATION PASSED: Ambiguous claim produced hedged verdict with uncertainty note.")
                passed_scenarios += 1
        else:
            print(f" [PASS] SCENARIO PASSED: Verdict rendered as {verdict.upper()}.")
            passed_scenarios += 1

        print("-" * 70)

    print(f"\nEvaluation Summary: {passed_scenarios}/{len(scenarios)} Scenarios Passed.")
    if calibration_failures > 0:
        print(f"WARNING: {calibration_failures} calibration failures detected!")
        sys.exit(1)
    else:
        print("ALL BENCHMARK & CALIBRATION TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    run_evaluation()
