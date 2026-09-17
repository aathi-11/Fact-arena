import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.claim_agent import normalize_claim
from src.agents.verify import verify_citations
from src.agents.judge_agent import judge
from src.graph.debate_graph import run_debate

def test_claim_decomposition():
    sub_claims = normalize_claim("Moderate coffee consumption reduces mortality and improves focus.")
    assert isinstance(sub_claims, list)
    assert len(sub_claims) >= 1

def test_verify_citations_clean():
    evidence_pool = {
        "E1": {"title": "Study 1", "url": "https://example.com/1", "snippet": "Evidence 1 snippet."},
        "E2": {"title": "Study 2", "url": "https://example.com/2", "snippet": "Evidence 2 snippet."}
    }
    pro_turns = [{"round": 1, "argument": "Supports claim [E1].", "cited_evidence_ids": ["E1"]}]
    con_turns = [{"round": 1, "argument": "Challenges claim [E2].", "cited_evidence_ids": ["E2"]}]

    report = verify_citations(pro_turns, con_turns, evidence_pool)
    assert report["is_clean"] is True
    assert "E1" in report["valid_citations"]
    assert "E2" in report["valid_citations"]
    assert len(report["hallucinated_citations"]) == 0

def test_verify_citations_hallucinated_injection():
    """
    Step 7 Guardrail Checkpoint: Manually inject fake evidence ID [E99] and assert
    that verify_citations flags the hallucination and judge incorporates guardrail warning.
    """
    evidence_pool = {
        "E1": {"title": "Study 1", "url": "https://example.com/1", "snippet": "Evidence 1 snippet."}
    }
    pro_turns = [{"round": 1, "argument": "Supports claim with fake study [E99].", "cited_evidence_ids": ["E99"]}]
    con_turns = [{"round": 1, "argument": "Valid challenge [E1].", "cited_evidence_ids": ["E1"]}]

    report = verify_citations(pro_turns, con_turns, evidence_pool)
    assert report["is_clean"] is False
    assert len(report["hallucinated_citations"]) == 1
    assert report["hallucinated_citations"][0]["cited_id"] == "E99"

    # Test judge reaction to hallucinated citation
    verdict = judge(
        claim="Test claim",
        sub_claims=["Test sub-claim"],
        pro_turns=pro_turns,
        con_turns=con_turns,
        evidence_pool=evidence_pool
    )
    assert verdict["guardrail_report"]["is_clean"] is False
    assert verdict["confidence"] <= 65
    assert "GUARDRAIL" in verdict["rationale"] or "uncited" in verdict["rationale"] or "hallucinated" in verdict["rationale"].lower() or "unverified" in verdict["uncertainty_note"].lower()

def test_full_debate_graph_execution():
    state = run_debate("Regular exercise reduces the risk of cardiovascular disease.", max_rounds=2)
    assert "claim" in state
    assert len(state["sub_claims"]) >= 1
    assert len(state["pro_turns"]) == 2
    assert len(state["con_turns"]) == 2
    assert isinstance(state["evidence_pool"], dict)
    assert state["verdict"] is not None
    assert "verdict" in state["verdict"]
    assert "confidence" in state["verdict"]
    assert "rationale" in state["verdict"]
    assert "total_seconds" in state["latency_log"]
