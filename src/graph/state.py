from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class DebateState(TypedDict):
    claim: str
    sub_claims: List[str]
    round: int
    max_rounds: int
    pro_turns: List[Dict[str, Any]]
    con_turns: List[Dict[str, Any]]
    evidence_pool: Dict[str, Dict[str, Any]]
    verdict: Optional[Dict[str, Any]]
    latency_log: Optional[Dict[str, Any]]
