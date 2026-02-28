"""
services/portfolio_generator.py — Portfolio HTML page generation.
"""

import logging
from typing import Optional

from services.llm_service import get_llm_response

logger = logging.getLogger(__name__)

_PORTFOLIO_PROMPT = """You are a senior front-end developer and UX writer.

Generate a clean, professional, self-contained HTML portfolio page for this candidate.

Candidate:
  Name: {full_name}
  Target Role: {target_role}
  Email: {email}
  LinkedIn: {linkedin}
  GitHub: {github}
  Education: {degree} — {college} ({grad_year})
  Skills: {skills}
  Projects:
{projects}
  Achievements: {achievements}

DESIGN REQUIREMENTS:
  - Self-contained single HTML file with ALL CSS embedded in <style> tags
  - Color palette: white (#ffffff) background, near-black (#111827) text,
    deep blue (#1d4ed8) accent, light gray (#f3f4f6) for card backgrounds
  - Font: system font stack — font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
  - Layout: centered container (max-width: 860px), generous padding
  - Sections: Hero, About, Projects (card grid), Skills (tag chips), Contact
  - Hero: candidate name as h1, one-line role tagline, contact links
  - Project cards: title, 1-sentence impact statement, tech tag row
  - Skills: small pill/chip labels, grouped by category
  - Contact: email, LinkedIn URL, GitHub URL — styled as plain links
  - Use CSS Grid or Flexbox for responsiveness — no JavaScript required
  - Clean section dividers (1px solid #e5e7eb)
  - Subtle box shadows on cards (box-shadow: 0 1px 3px rgba(0,0,0,0.08))
  - No emojis in the HTML body
  - Use the candidate's actual data — no placeholder text

STRICT OUTPUT RULE: Return ONLY valid HTML starting with <!DOCTYPE html>.
No backticks, no markdown, no explanation before or after.
"""


def generate_portfolio(data: dict) -> tuple[str, Optional[str]]:
    """
    Generate a self-contained HTML portfolio page.

    Parameters
    ----------
    data : dict
        Candidate data from the UI form.

    Returns
    -------
    (html_text, error)
    """
    prompt = _PORTFOLIO_PROMPT.format(
        full_name=data["full_name"],
        target_role=data["target_role"],
        email=data["email"],
        linkedin=data.get("linkedin", ""),
        github=data.get("github", ""),
        degree=data["degree"],
        college=data["college"],
        grad_year=data["grad_year"],
        skills=data["skills"],
        projects=data["projects"],
        achievements=data.get("achievements") or "None",
    )
    logger.info("Generating portfolio HTML for: %s", data["full_name"])
    return get_llm_response(prompt)
