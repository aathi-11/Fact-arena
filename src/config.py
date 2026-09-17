import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Groq Model Selection (Active high-speed models on Groq LPUs)
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "openai/gpt-oss-120b")
DEBATER_MODEL = os.getenv("DEBATER_MODEL", "qwen/qwen3.8-27b")

# Debate Configuration Defaults (Optimized for speed & token rate limits)
MAX_DEBATE_ROUNDS = 1
MAX_EVIDENCE_PER_TURN = 3
