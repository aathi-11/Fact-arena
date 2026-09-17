CLAIM_DECOMPOSITION_PROMPT = """You are an expert fact-checker and logical analyst.
Your task is to take a raw claim and break it down into 1 to 3 atomic, clear, testable, and checkable sub-claims.

Instructions:
1. Each sub-claim must be self-contained and verifiable with empirical evidence.
2. Remove subjective vagueness and break compound assertions into single logical statements.
3. Respond ONLY with a valid JSON object containing a "sub_claims" array.

Example Input:
"Moderate coffee consumption causes heart disease and reduces lifespan."

Example Output:
{{
  "sub_claims": [
    "Moderate coffee consumption is correlated with increased risk of cardiovascular disease.",
    "Coffee drinking reduces overall human lifespan."
  ]
}}

Raw Claim to decompose:
"{raw_claim}"
"""
