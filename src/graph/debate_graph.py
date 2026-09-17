import time
import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from src.graph.state import DebateState
from src.agents.claim_agent import normalize_claim
from src.agents.pro_agent import argue_pro
from src.agents.con_agent import argue_con
from src.agents.judge_agent import judge
from src.config import MAX_DEBATE_ROUNDS

logger = logging.getLogger(__name__)

# Node functions
def node_normalize(state: DebateState) -> Dict[str, Any]:
    t0 = time.time()
    raw_claim = state["claim"]
    sub_claims = normalize_claim(raw_claim)
    elapsed = time.time() - t0
    
    latency = state.get("latency_log") or {}
    latency["normalize_seconds"] = round(elapsed, 3)
    
    return {
        "sub_claims": sub_claims,
        "latency_log": latency
    }

def node_pro_turn(state: DebateState) -> Dict[str, Any]:
    t0 = time.time()
    current_round = state.get("round", 1)
    claim = state["claim"]
    evidence_pool = state.get("evidence_pool") or {}
    pro_turns = state.get("pro_turns") or []
    con_turns = state.get("con_turns") or []
    
    prior_turns = []
    # Combine prior turns in order
    max_r = max([t.get("round", 1) for t in pro_turns + con_turns] or [0])
    for r in range(1, max_r + 1):
        for pt in [t for t in pro_turns if t.get("round") == r]:
            prior_turns.append(pt)
        for ct in [t for t in con_turns if t.get("round") == r]:
            prior_turns.append(ct)
            
    turn_res = argue_pro(claim=claim, evidence_pool=evidence_pool, prior_turns=prior_turns)
    turn_res["round"] = current_round
    
    updated_pro_turns = pro_turns + [turn_res]
    elapsed = time.time() - t0
    
    latency = state.get("latency_log") or {}
    pro_l = latency.get("pro_turns_seconds", [])
    pro_l.append(round(elapsed, 3))
    latency["pro_turns_seconds"] = pro_l

    return {
        "pro_turns": updated_pro_turns,
        "evidence_pool": evidence_pool,
        "latency_log": latency
    }

def node_con_turn(state: DebateState) -> Dict[str, Any]:
    t0 = time.time()
    current_round = state.get("round", 1)
    claim = state["claim"]
    evidence_pool = state.get("evidence_pool") or {}
    pro_turns = state.get("pro_turns") or []
    con_turns = state.get("con_turns") or []
    
    prior_turns = []
    max_r = max([t.get("round", 1) for t in pro_turns + con_turns] or [0])
    for r in range(1, max_r + 1):
        for pt in [t for t in pro_turns if t.get("round") == r]:
            prior_turns.append(pt)
        for ct in [t for t in con_turns if t.get("round") == r]:
            prior_turns.append(ct)
            
    turn_res = argue_con(claim=claim, evidence_pool=evidence_pool, prior_turns=prior_turns)
    turn_res["round"] = current_round
    
    updated_con_turns = con_turns + [turn_res]
    elapsed = time.time() - t0
    
    latency = state.get("latency_log") or {}
    con_l = latency.get("con_turns_seconds", [])
    con_l.append(round(elapsed, 3))
    latency["con_turns_seconds"] = con_l

    return {
        "con_turns": updated_con_turns,
        "evidence_pool": evidence_pool,
        "latency_log": latency
    }

def route_next_turn(state: DebateState) -> Literal["advance_round", "judge"]:
    current_round = state.get("round", 1)
    max_rounds = state.get("max_rounds", MAX_DEBATE_ROUNDS)
    if current_round < max_rounds:
        return "advance_round"
    return "judge"

def node_advance_round(state: DebateState) -> Dict[str, Any]:
    current_round = state.get("round", 1)
    return {"round": current_round + 1}

def node_judge(state: DebateState) -> Dict[str, Any]:
    t0 = time.time()
    claim = state["claim"]
    sub_claims = state.get("sub_claims", [])
    pro_turns = state.get("pro_turns", [])
    con_turns = state.get("con_turns", [])
    evidence_pool = state.get("evidence_pool", {})
    
    verdict_res = judge(
        claim=claim,
        sub_claims=sub_claims,
        pro_turns=pro_turns,
        con_turns=con_turns,
        evidence_pool=evidence_pool
    )
    
    elapsed = time.time() - t0
    latency = state.get("latency_log") or {}
    latency["judge_seconds"] = round(elapsed, 3)
    
    total_time = (
        latency.get("normalize_seconds", 0) +
        sum(latency.get("pro_turns_seconds", [])) +
        sum(latency.get("con_turns_seconds", [])) +
        latency.get("judge_seconds", 0)
    )
    latency["total_seconds"] = round(total_time, 3)

    return {
        "verdict": verdict_res,
        "latency_log": latency
    }

# Build LangGraph State Graph
def build_debate_graph():
    builder = StateGraph(DebateState)
    
    builder.add_node("normalize", node_normalize)
    builder.add_node("pro_turn", node_pro_turn)
    builder.add_node("con_turn", node_con_turn)
    builder.add_node("advance_round", node_advance_round)
    builder.add_node("judge", node_judge)
    
    builder.set_entry_point("normalize")
    
    builder.add_edge("normalize", "pro_turn")
    builder.add_edge("pro_turn", "con_turn")
    
    builder.add_conditional_edges(
        "con_turn",
        route_next_turn,
        {
            "advance_round": "advance_round",
            "judge": "judge"
        }
    )
    builder.add_edge("advance_round", "pro_turn")
    builder.add_edge("judge", END)
    
    return builder.compile()

_COMPILED_GRAPH = None

def get_debate_graph():
    global _COMPILED_GRAPH
    if _COMPILED_GRAPH is None:
        _COMPILED_GRAPH = build_debate_graph()
    return _COMPILED_GRAPH

def run_debate(claim: str, max_rounds: int = MAX_DEBATE_ROUNDS) -> DebateState:
    """
    Main entry point to execute a full multi-agent debate and fact-checking graph.
    """
    initial_state: DebateState = {
        "claim": claim,
        "sub_claims": [],
        "round": 1,
        "max_rounds": max_rounds,
        "pro_turns": [],
        "con_turns": [],
        "evidence_pool": {},
        "verdict": None,
        "latency_log": {}
    }
    
    graph = get_debate_graph()
    final_state = graph.invoke(initial_state)
    return final_state
