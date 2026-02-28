"""
services/cover_letter_generator.py — Cover letter generation.

Prompt templates and generation logic isolated here.
"""

import logging
from datetime import datetime
from typing import Optional

from services.llm_service import get_llm_response

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are a professional career coach who writes precise, persuasive cover letters. "
    "Your letters are direct and confident — never desperate, never dramatic. "
    "You avoid all clichés: no 'I am passionate', no 'dream company', no 'synergy', "
    "no 'I believe I would be a great fit'. Each letter opens with a specific, grounded "
    "claim, not a hollow opener."
)

_COVER_LETTER_PROMPT = """{system}

---
Task: Write a tailored cover letter for the role of {target_role}.

Candidate background:
  Name: {full_name}
  Target Role: {target_role}
  Education: {degree} — {college} ({grad_year})
  Skills: {skills}
  Key Projects: {projects}
  Internships: {internships}
  Achievements: {achievements}
{jd_block}
Date: {date}

STRUCTURE (follow exactly):
  Paragraph 1 (2–3 sentences): State the role. Open with one specific, confident claim
    that immediately establishes value — draw from a concrete project outcome or metric.
  Paragraph 2 (3–4 sentences): Connect 1–2 projects directly to what this role likely
    requires. Use outcomes, not feature lists.
  Paragraph 3 (2–3 sentences): Reference one concrete achievement or internship result.
    Show what kind of contributor they are, not just what they did.
  Closing (1–2 sentences): Brief, assertive close. Offer to discuss further. No adjectives.

CONSTRAINTS:
  - 300–400 words total
  - No clichés, no "I am passionate/excited/driven"
  - No personal pronouns at sentence starts where avoidable
  - Professional, calm, direct tone
  - No emojis
  - Return ONLY the cover letter — no subject line, no file name, no preamble

Opening line: "Dear Hiring Manager,"
Closing line: "Sincerely,\\n{full_name}"
"""


def generate_cover_letter(
    data: dict,
    job_description: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """
    Generate a tailored cover letter.

    Parameters
    ----------
    data : dict
        Candidate data from the UI form.
    job_description : str or None
        Optional JD text to reference in the letter.

    Returns
    -------
    (cover_letter_text, error)
    """
    if job_description and job_description.strip():
        jd_block = (
            f"\nJob Description (use to align letter):\n"
            f"---\n{job_description.strip()}\n---"
        )
    else:
        jd_block = ""

    prompt = _COVER_LETTER_PROMPT.format(
        system=_SYSTEM,
        target_role=data["target_role"],
        full_name=data["full_name"],
        degree=data["degree"],
        college=data["college"],
        grad_year=data["grad_year"],
        skills=data["skills"],
        projects=data["projects"],
        internships=data.get("internships") or "None",
        achievements=data.get("achievements") or "None",
        jd_block=jd_block,
        date=datetime.now().strftime("%B %d, %Y"),
    )

    logger.info("Generating cover letter for: %s", data["target_role"])
    return get_llm_response(prompt)
