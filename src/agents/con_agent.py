import logging
from typing import List, Dict, Any
from src.config import GROQ_API_KEY, DEBATER_MODEL, MAX_EVIDENCE_PER_TURN
from src.retrieval.web_search import search
from src.prompts.debater_prompt import get_debater_prompt
from src.agents.groq_client import call_groq_with_retry

logger = logging.getLogger(__name__)

def argue_con(claim: str, evidence_pool: Dict[str, Dict[str, Any]], prior_turns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Executes a Con debater turn with rate-limit resilient Groq client calls.
    """
    # 1. Reformulate stance-conditioned query
    query = f"{claim} refuting counter-evidence risks health harm false debate study"
    new_evidence = search(query=query, max_results=MAX_EVIDENCE_PER_TURN)

    # 2. Add new evidence to evidence_pool
    newly_added_ids = []
    for item in new_evidence:
        existing_id = None
        for eid, ev in evidence_pool.items():
            if ev.get("url") == item.get("url") or ev.get("snippet") == item.get("snippet"):
                existing_id = eid
                break
        
        if existing_id:
            newly_added_ids.append(existing_id)
        else:
            new_id = f"E{len(evidence_pool) + 1}"
            evidence_pool[new_id] = {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", "")
            }
            newly_added_ids.append(new_id)

    # 3. Format evidence set for prompt
    evidence_lines = []
    for eid, ev in evidence_pool.items():
        evidence_lines.append(f"[{eid}] {ev['title']}: {ev['snippet']} (Source: {ev['url']})")
    evidence_text = "\n".join(evidence_lines)

    # 4. Format prior transcript
    transcript_lines = []
    for t in prior_turns:
        role = t.get("role", "Debater").upper()
        transcript_lines.append(f"[{role} Round {t.get('round', 1)}]: {t.get('argument', '')}")
    prior_transcript = "\n".join(transcript_lines)

    # 5. Call LLM with retry client or Fallback
    prompt = get_debater_prompt(stance="con", claim=claim, evidence_text=evidence_text, prior_transcript=prior_transcript)

    if GROQ_API_KEY:
        try:
            data = call_groq_with_retry(model=DEBATER_MODEL, prompt=prompt, temperature=0.2)
            argument = data.get("argument", "")
            cited_ids = data.get("cited_evidence_ids", [])
            return {
                "role": "con",
                "argument": argument,
                "cited_evidence_ids": cited_ids,
                "evidence_used": [evidence_pool[eid] for eid in cited_ids if eid in evidence_pool]
            }
        except Exception as e:
            logger.warning(f"Groq con_agent call failed: {e}. Using structured fallback.")

    # Fallback response using available evidence IDs
    cited = [eid for eid in newly_added_ids if eid in evidence_pool][:2]
    citations_str = " ".join([f"[{eid}]" for eid in cited])
    fallback_arg = (
        f"Significant counter-evidence challenges the assertion '{claim}'. "
        f"Observational and empirical data refute the generalization {citations_str}. "
        f"Methodological flaws and confounding variables undermine the supporting position."
    )
    return {
        "role": "con",
        "argument": fallback_arg,
        "cited_evidence_ids": cited,
        "evidence_used": [evidence_pool[eid] for eid in cited if eid in evidence_pool]
    }
