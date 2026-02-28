"""
services/resume_generator.py — Resume generation with two modes:

  1. Standard:  generate_resume(data)
  2. JD-tailored: generate_resume(data, job_description="...")
  3. Improvement from uploaded resume: improve_resume(raw_text, job_description=None)

All prompt templates live in this module.
"""

import logging
from typing import Optional

from services.llm_service import get_llm_response

logger = logging.getLogger(__name__)

# ── System persona (shared) ───────────────────────────────────────────────────
_SYSTEM = (
    "You are a senior technical recruiter and professional resume writer with 15 years of "
    "experience placing engineers and data scientists at top-tier tech firms. "
    "You write resumes that consistently get shortlisted. "
    "Your writing is sharp, specific, and always quantified — never vague, never generic. "
    "You never use the following phrases or their variants: "
    "'passionate', 'motivated', 'results-driven', 'hardworking', 'dedicated', "
    "'team player', 'go-getter', 'self-starter', 'dynamic', 'detail-oriented', "
    "'synergy', 'leverage', 'empower', 'innovative', 'cutting-edge'. "
    "Every claim you write is either measurable or verifiable."
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_candidate(data: dict) -> str:
    """Serialise candidate dict to a clean text block for use in prompts."""
    return f"""
Name : {data['full_name']}
Email: {data['email']}   Phone: {data['phone']}
LinkedIn: {data.get('linkedin', 'N/A')}   GitHub: {data.get('github', 'N/A')}

Education:
  {data['degree']} — {data['college']}
  Graduation Year: {data['grad_year']}   CGPA/Score: {data.get('cgpa', 'N/A')}

Technical Skills:
  {data['skills']}

Projects:
{data['projects']}

Internships / Experience:
{data.get('internships') or 'None'}

Achievements / Extra-curriculars:
{data.get('achievements') or 'None'}

Target Role : {data['target_role']}
Experience Level : {data['experience_level']}
""".strip()


# ── Prompt templates ──────────────────────────────────────────────────────────

_STANDARD_PROMPT = """{system}

---
Task: Generate a professional, ATS-optimised resume for the role: {target_role}

Candidate details:
{candidate}

HARD CONSTRAINTS:
1. Use this EXACT section order (in ALL CAPS):
   PROFESSIONAL SUMMARY / TECHNICAL SKILLS / PROJECTS / INTERNSHIPS & EXPERIENCE / EDUCATION / ACHIEVEMENTS
2. Professional Summary: exactly 3 sentences. Sentence 1 = role + years of experience context.
   Sentence 2 = strongest technical capability. Sentence 3 = standout project or outcome.
3. Technical Skills: group into categories separated by pipe — e.g. "Languages: Python, Java | Frameworks: ..."
4. Each Project bullet: <strong action verb> + <what> + <how (tech)> + <outcome with number>
5. Expand thin descriptions with realistic inferred metrics (users, accuracy %, time saved, etc.)
6. Rewrite any vague language into precise, professional statements.
7. No emojis, no markdown symbols (no **, no ##), no asterisks.
8. Bullets prefixed with a plain hyphen ( - ).
9. Resume body must fit on a single A4 page (≈550–650 words max).
10. Return ONLY the resume text. No preamble, no "Here is your resume", no closing note.

HEADER FORMAT (first two lines, exactly):
{full_name}
{email} | {phone} | {linkedin} | {github}
"""

_JD_TAILORED_PROMPT = """{system}

---
Task: Generate a JD-tailored, ATS-optimised resume for:  {target_role}

--- JOB DESCRIPTION ---
{job_description}
--- END JD ---

Candidate details:
{candidate}

ADDITIONAL JD-TAILORING INSTRUCTIONS:
1. Extract required skills and keywords from the JD above.
2. Naturally incorporate matching keywords into the summary, skills, and project bullets.
3. Lead with skills/experience most relevant to this specific JD.
4. Reorder project bullets so the most JD-relevant outcomes appear first.
5. If a JD keyword is genuinely present in the candidate's background, use it — otherwise omit it.
   Never fabricate experience, never keyword-stuff.
6. Adjust the summary's second and third sentence to directly address the JD's core requirements.

HARD CONSTRAINTS (same as standard):
1. Section order (ALL CAPS): PROFESSIONAL SUMMARY / TECHNICAL SKILLS / PROJECTS /
   INTERNSHIPS & EXPERIENCE / EDUCATION / ACHIEVEMENTS
2. Professional Summary: 3 sentences aligned to the JD.
3. Bullets prefixed with a plain hyphen ( - ).
4. No emojis, no markdown symbols, no asterisks.
5. Single A4 page worth of content (≈550–650 words).
6. Return ONLY the resume text.

HEADER FORMAT (first two lines, exactly):
{full_name}
{email} | {phone} | {linkedin} | {github}
"""

_IMPROVE_PROMPT = """{system}

---
Task: Improve and professionally rewrite this uploaded resume{jd_clause}.

--- UPLOADED RESUME ---
{raw_text}
--- END RESUME ---
{jd_block}

INSTRUCTIONS:
1. Preserve all factual information; do not fabricate new experience.
2. Rewrite weak, vague, or passive bullets into strong action-verb statements with measurable outcomes.
3. Remove filler language, meaningless buzzwords, and repetition.
4. Ensure ATS-friendly formatting: plain text, standard section headers in ALL CAPS.
5. Improve the Professional Summary to be role-specific and concrete.
6. Group Technical Skills into labelled categories.
7. Keep the same section order:
   PROFESSIONAL SUMMARY / TECHNICAL SKILLS / PROJECTS / INTERNSHIPS & EXPERIENCE / EDUCATION / ACHIEVEMENTS
8. No emojis, no markdown symbols, bullets prefixed with plain hyphen ( - ).
9. Return ONLY the improved resume text.
"""


# ── Public API ────────────────────────────────────────────────────────────────

def generate_resume(
    data: dict,
    job_description: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """
    Generate an ATS-optimised resume from form data.

    Parameters
    ----------
    data : dict
        Structured candidate data collected from the UI form.
    job_description : str or None
        If provided, switches to JD-tailored generation mode.

    Returns
    -------
    (resume_text, error) — error is None on success.
    """
    candidate_block = _format_candidate(data)

    if job_description and job_description.strip():
        logger.info("Generating JD-tailored resume for: %s", data['target_role'])
        prompt = _JD_TAILORED_PROMPT.format(
            system=_SYSTEM,
            target_role=data["target_role"],
            job_description=job_description.strip(),
            candidate=candidate_block,
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            linkedin=data.get("linkedin", ""),
            github=data.get("github", ""),
        )
    else:
        logger.info("Generating standard resume for: %s", data['target_role'])
        prompt = _STANDARD_PROMPT.format(
            system=_SYSTEM,
            target_role=data["target_role"],
            candidate=candidate_block,
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            linkedin=data.get("linkedin", ""),
            github=data.get("github", ""),
        )

    return get_llm_response(prompt)


def improve_resume(
    raw_text: str,
    job_description: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """
    Rewrite and improve an uploaded resume's text.

    Parameters
    ----------
    raw_text : str
        Text extracted from the uploaded PDF/DOCX.
    job_description : str or None
        Optional JD to tailor the improvement toward.

    Returns
    -------
    (improved_text, error)
    """
    if job_description and job_description.strip():
        jd_clause = " and tailor it to the job description below"
        jd_block = (
            f"\n--- JOB DESCRIPTION ---\n{job_description.strip()}\n--- END JD ---\n"
        )
    else:
        jd_clause = ""
        jd_block = ""

    # Cap raw text to avoid blowing the context window.
    # 6 000 chars ≈ ~1 500 tokens — leaves plenty of room for the improved output.
    MAX_RAW = 6_000
    if len(raw_text) > MAX_RAW:
        logger.warning(
            "Uploaded resume text truncated from %d → %d chars for LLM prompt",
            len(raw_text), MAX_RAW,
        )
        raw_text = raw_text[:MAX_RAW]

    prompt = _IMPROVE_PROMPT.format(
        system=_SYSTEM,
        jd_clause=jd_clause,
        raw_text=raw_text,
        jd_block=jd_block,
    )
    logger.info("Improving uploaded resume (raw len=%d)", len(raw_text))
    return get_llm_response(prompt)
