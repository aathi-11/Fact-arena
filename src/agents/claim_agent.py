import logging
from typing import List
from src.config import GROQ_API_KEY, DEBATER_MODEL
from src.prompts.claim_prompt import CLAIM_DECOMPOSITION_PROMPT
from src.agents.groq_client import call_groq_with_retry

logger = logging.getLogger(__name__)

def normalize_claim(raw_claim: str) -> List[str]:
    """
    Decomposes a raw user claim into 1 to 3 atomic, checkable sub-claims.
    """
    if GROQ_API_KEY:
        try:
            prompt = CLAIM_DECOMPOSITION_PROMPT.format(raw_claim=raw_claim)
            data = call_groq_with_retry(model=DEBATER_MODEL, prompt=prompt, temperature=0.1)
            
            if isinstance(data, dict) and "sub_claims" in data and isinstance(data["sub_claims"], list):
                return data["sub_claims"]
            elif isinstance(data, list):
                return data
            elif isinstance(data, dict):
                for val in data.values():
                    if isinstance(val, list):
                        return val
        except Exception as e:
            logger.warning(f"Groq claim normalization call failed: {e}. Falling back to default decomposition.")

    # Fallback normalization logic
    parts = [p.strip() for p in raw_claim.split(" and ") if p.strip()]
    if len(parts) > 1:
        return [f"Claim element {i+1}: {p}" for i, p in enumerate(parts[:3])]
    return [raw_claim.strip()]
