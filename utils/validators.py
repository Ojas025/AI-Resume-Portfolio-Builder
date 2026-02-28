"""
utils/validators.py — Input validation for form data.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_REQUIRED_FIELDS: dict[str, str] = {
    "full_name":   "Full Name",
    "email":       "Email",
    "phone":       "Phone",
    "degree":      "Degree",
    "college":     "College / University",
    "skills":      "Technical Skills",
    "projects":    "Projects",
    "target_role": "Target Role",
}

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_form_data(data: dict) -> list[str]:
    """
    Validate structured candidate form data.

    Parameters
    ----------
    data : dict
        Candidate data from the UI form.

    Returns
    -------
    list[str] — list of human-readable error messages; empty if valid.
    """
    errors: list[str] = []

    for field, label in _REQUIRED_FIELDS.items():
        if not str(data.get(field, "")).strip():
            errors.append(f"{label} is required.")

    email = data.get("email", "").strip()
    if email and not _EMAIL_RE.match(email):
        errors.append("Email address does not appear to be valid.")

    grad_year = data.get("grad_year")
    try:
        year = int(grad_year)
        if not (1990 <= year <= 2035):
            errors.append("Graduation year must be between 1990 and 2035.")
    except (TypeError, ValueError):
        errors.append("Graduation year must be a valid integer.")

    if errors:
        logger.warning("Validation failed: %s", errors)

    return errors


def validate_api_key(key: Optional[str]) -> Optional[str]:
    """
    Return an error string if the API key looks obviously wrong, else None.

    Parameters
    ----------
    key : str or None

    Returns
    -------
    str or None
    """
    if not key or not key.strip():
        return "GEMINI_API_KEY is not set. Add it to .env or the sidebar."
    if len(key.strip()) < 20:
        return "API key looks too short — please verify it."
    return None
