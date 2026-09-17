import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Groq Model Selection (Active models available on Groq LPUs)
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "openai/gpt-oss-120b")
DEBATER_MODEL = os.getenv("DEBATER_MODEL", "openai/gpt-oss-20b")

# Debate Configuration Defaults
MAX_DEBATE_ROUNDS = 3
MAX_EVIDENCE_PER_TURN = 5
