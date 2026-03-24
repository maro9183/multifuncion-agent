import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

WORKSPACE = BASE_DIR / "workspace"
LOGS = BASE_DIR / "logs"
MEMORY = BASE_DIR / "memory"

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
