import logging
import re
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

def verify_citations(
    pro_turns: List[Dict[str, Any]],
    con_turns: List[Dict[str, Any]],
    evidence_pool: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Scans all arguments in pro_turns and con_turns for cited evidence IDs (e.g., [E1], [E99]).
    Validates each cited ID against the evidence_pool.
    Flags invalid/hallucinated citations and returns a guardrail report dict.
    """
    valid_citations = set()
    hallucinated_citations = []
    turn_reports = []

    all_turns = []
    for turn in pro_turns:
        all_turns.append(("PRO", turn))
    for turn in con_turns:
        all_turns.append(("CON", turn))

    for stance, turn in all_turns:
        arg_text = turn.get("argument", "")
        cited_in_turn = turn.get("cited_evidence_ids", [])
        
        # Regex find any tags like [E1], [E2], [E99] in argument text
        regex_matches = re.findall(r'\[(E\d+)\]', arg_text)
        combined_citations = list(set(cited_in_turn + regex_matches))
        
        valid_for_turn = []
        invalid_for_turn = []
        
        for cid in combined_citations:
            if cid in evidence_pool:
                valid_citations.add(cid)
                valid_for_turn.append(cid)
            else:
                invalid_for_turn.append(cid)
                hallucinated_citations.append({
                    "stance": stance,
                    "turn_round": turn.get("round", 1),
                    "cited_id": cid,
                    "snippet": arg_text[:120] + "..."
                })
                logger.warning(
                    f"GUARDRAIL TRIGGERED: {stance} agent hallucinated cited evidence ID [{cid}] "
                    f"which does not exist in evidence pool!"
                )
                
        turn_reports.append({
            "stance": stance,
            "round": turn.get("round", 1),
            "valid_citations": valid_for_turn,
            "invalid_citations": invalid_for_turn,
            "has_hallucination": len(invalid_for_turn) > 0
        })

    is_clean = len(hallucinated_citations) == 0
    warning_summary = ""
    if not is_clean:
        bad_ids = ", ".join(sorted(set([h["cited_id"] for h in hallucinated_citations])))
        warning_summary = (
            f"WARNING: Citation Integrity Violation Detected! Debater agent cited non-existent evidence ID(s): [{bad_ids}]. "
            f"These uncited assertions MUST be discounted from judicial evaluation."
        )

    return {
        "is_clean": is_clean,
        "valid_citations": sorted(list(valid_citations)),
        "hallucinated_citations": hallucinated_citations,
        "turn_reports": turn_reports,
        "warning_summary": warning_summary
    }
