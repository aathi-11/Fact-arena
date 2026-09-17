import time
import logging
import json
from typing import Dict, Any, Optional
from groq import Groq
from src.config import GROQ_API_KEY

logger = logging.getLogger(__name__)

def call_groq_with_retry(
    model: str,
    prompt: str,
    temperature: float = 0.1,
    max_retries: int = 3,
    fallback_model: Optional[str] = "groq/compound-mini"
) -> Dict[str, Any]:
    """
    Executes a Groq chat completion call with automatic rate-limit (429) retries and model fallback.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set")

    client = Groq(api_key=GROQ_API_KEY)
    target_models = [model]
    if fallback_model and fallback_model != model:
        target_models.append(fallback_model)

    for m in target_models:
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=m,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content.strip()
                return json.loads(content)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "rate_limit" in err_str.lower() or "limit" in err_str.lower():
                    wait_time = (attempt + 1) * 3
                    logger.warning(
                        f"Groq rate limit (429) encountered for model '{m}'. "
                        f"Sleeping {wait_time}s before retry {attempt + 1}/{max_retries}..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.warning(f"Groq call for model '{m}' failed: {e}")
                    break  # Try next fallback model if non-rate-limit error

    raise RuntimeError(f"All Groq model attempts failed for primary model '{model}'")
