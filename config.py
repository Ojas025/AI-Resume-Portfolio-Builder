"""
config.py — Centralised application configuration.
All tuneable constants and environment-sourced settings live here.
"""

import os
import logging

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - depends on local install state
    def load_dotenv() -> bool:
        return False

load_dotenv()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Gemini ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_FALLBACK_MODELS: list[str] = [
    model.strip()
    for model in os.getenv("GEMINI_FALLBACK_MODELS", "gemini-2.5-flash-lite").split(",")
    if model.strip() and model.strip() != GEMINI_MODEL
]
GEMINI_FALLBACK_MODEL: str = GEMINI_FALLBACK_MODELS[0] if GEMINI_FALLBACK_MODELS else ""
LLM_TEMPERATURE: float = 0.70
LLM_TOP_P: float = 0.92
LLM_MAX_TOKENS: int = 8192

# ── App ──────────────────────────────────────────────────────────────────────
APP_TITLE: str = "AI Resume & Portfolio Builder"
APP_ICON: str = "⬛"  # minimal icon
APP_VERSION: str = "2.0.0"

# ── Experience level choices ─────────────────────────────────────────────────
EXPERIENCE_LEVELS: list[str] = [
    "Fresher / Entry-level (0–1 yr)",
    "Junior (1–2 yrs)",
    "Mid-level (2–4 yrs)",
    "Senior (4+ yrs)",
]

# ── Demo / example data ──────────────────────────────────────────────────────
EXAMPLE_DATA: dict = {
    "full_name": "Rahul Mehta",
    "email": "arjun.mehta@gmail.com",
    "phone": "+91-98765-43210",
    "linkedin": "linkedin.com/in/arjunmehta",
    "github": "github.com/arjunmehta",
    "degree": "B.Tech Computer Science (AI & ML)",
    "college": "Vellore Institute of Technology",
    "grad_year": 2025,
    "cgpa": "8.7",
    "skills": (
        "Python, TensorFlow, PyTorch, Scikit-learn, FastAPI, "
        "React, SQL, MongoDB, Docker, Git, AWS"
    ),
    "projects": (
        "1. SentimentScope – Real-time Twitter sentiment analyser using BERT fine-tuned on "
        "50k tweets; achieved 91% accuracy; deployed via FastAPI with 200ms latency | "
        "Python, HuggingFace, FastAPI, Redis\n"
        "2. CropGuard – Disease detection app for farmers using CNN (ResNet50), detects "
        "38 crop diseases from leaf photos; Android app with offline inference | "
        "PyTorch, OpenCV, Flutter\n"
        "3. StockSeer – LSTM-based stock price predictor with live NSE data integration; "
        "built interactive dashboard with 1-week forecast | Python, Keras, Plotly, Yahoo Finance API"
    ),
    "internships": (
        "ML Engineering Intern – Infosys (May–Aug 2024): Built automated invoice extraction "
        "pipeline using LayoutLM, reduced manual processing by 70%."
    ),
    "achievements": (
        "Smart India Hackathon 2023 – National Finalist (Top 10/1200 teams)\n"
        "Google DSC Lead – organized 6 workshops, 400+ student participants\n"
        "LeetCode: 650+ problems solved, max contest rating 1842"
    ),
    "target_role": "Machine Learning Engineer",
    "experience_level": "Fresher / Entry-level (0–1 yr)",
}
