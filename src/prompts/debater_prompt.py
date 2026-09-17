def get_debater_prompt(stance: str, claim: str, evidence_text: str, prior_transcript: str) -> str:
    """
    Generates a stance-conditioned debater prompt.
    stance: 'pro' or 'con'
    """
    stance_desc = "SUPPORT and AFFIRM" if stance.lower() == "pro" else "CHALLENGE, REFUTE, and DISPROVE"
    
    return f"""You are a precise, evidence-bound adversarial debater operating in a high-stakes fact-checking tournament.
Your stance is {stance.upper()}: you must {stance_desc} the claim based STRICTLY AND EXCLUSIVELY on the provided evidence snippets below.

RULES OF ENGAGEMENT:
1. Every factual assertion or argument point MUST cite an evidence ID from the provided evidence list using the tag format [E1], [E2], etc.
2. STRICT EVIDENCE GROUNDING: You are FORBIDDEN from asserting any fact, statistic, or claim that is not explicitly traceable to one of the provided evidence snippets below. Do not use outside knowledge.
3. If the provided evidence is weak or unsupportive of your stance, frame the available evidence as strongly as logically possible without inventing facts.
4. Directly counter prior opponent arguments if any exist in the debate transcript.

STRICT OUTPUT FORMAT:
You must return your output strictly as a JSON object with this exact structure:
{{
  "argument": "<your detailed argument incorporating cited evidence tags like [E1], [E2]>",
  "cited_evidence_ids": ["E1", "E2"]
}}

Target Claim: "{claim}"

Prior Debate Transcript:
{prior_transcript if prior_transcript else "No prior turns. This is the opening argument."}

Available Evidence Set:
{evidence_text}

Respond ONLY with valid JSON.
"""
