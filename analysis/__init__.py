# ============================================================
# analysis/__init__.py
# PUBLIC EXPORTS FOR THE NEW CONFIG-DRIVEN ARCHITECTURE
# ============================================================

# -----------------------------
# ROLE CONFIG (Unified)
# -----------------------------
from .model_config import ROLE_CONFIG

# -----------------------------
# UNIVERSAL MODEL ENGINE
# -----------------------------
from .model_engine import run_model

# -----------------------------
# SUMMARY FUNCTIONS
# -----------------------------
from .summaries import (
    generate_gk_summary,
    generate_winger_summary,
    generate_midfielder_summary,
    generate_striker_summary,
)

# -----------------------------
# OPTIONAL HELPER
# -----------------------------
def get_role_config(role: str):
    """Retrieve the full configuration for a given role."""
    return ROLE_CONFIG.get(role.lower())


# -----------------------------
# PUBLIC API
# -----------------------------
__all__ = [
    # Unified configuration
    "ROLE_CONFIG",
    "get_role_config",

    # Engine
    "run_model",

    # Summaries
    "generate_gk_summary",
    "generate_winger_summary",
    "generate_midfielder_summary",
    "generate_striker_summary",
]
