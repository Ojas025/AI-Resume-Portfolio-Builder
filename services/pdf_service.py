"""
services/pdf_service.py — ReportLab PDF rendering.

Converts plain-text resume output (from the LLM) into a clean,
typeset PDF document.  The parser identifies headings, bullets,
name/contact lines by pattern rather than position so it works
robustly regardless of model output variation.
"""

import io
import re
import logging
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY

logger = logging.getLogger(__name__)

# ── Colour palette ─────────────────────────────────────────────────────────────
_ACCENT = colors.HexColor("#1d4ed8")   # deep blue
_BODY   = colors.HexColor("#111827")   # near-black
_MUTED  = colors.HexColor("#6b7280")   # gray
_RULE   = colors.HexColor("#e5e7eb")   # light rule

# ── Section headers that trigger blue-styled heading blocks ───────────────────
_SECTION_KEYWORDS = frozenset({
    "PROFESSIONAL SUMMARY", "SUMMARY",
    "TECHNICAL SKILLS", "SKILLS",
    "PROJECTS",
    "INTERNSHIPS & EXPERIENCE", "INTERNSHIPS", "EXPERIENCE",
    "EDUCATION",
    "ACHIEVEMENTS", "CERTIFICATIONS",
    "AWARDS",
})

# ── ReportLab paragraph styles ────────────────────────────────────────────────
def _build_styles() -> dict:
    BF = "Helvetica-Bold"
    NF = "Helvetica"
    return {
        "name": ParagraphStyle(
            "name", fontName=BF, fontSize=18, leading=22,
            textColor=_BODY, alignment=TA_LEFT, spaceAfter=2,
        ),
        "contact": ParagraphStyle(
            "contact", fontName=NF, fontSize=8.5, leading=12,
            textColor=_MUTED, alignment=TA_LEFT, spaceAfter=6,
        ),
        "section": ParagraphStyle(
            "section", fontName=BF, fontSize=8.5, leading=11,
            textColor=_ACCENT, spaceBefore=10, spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "body", fontName=NF, fontSize=9, leading=13,
            textColor=_BODY, alignment=TA_JUSTIFY, spaceAfter=2,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName=NF, fontSize=9, leading=13,
            textColor=_BODY, leftIndent=14, spaceAfter=2,
        ),
    }


def create_pdf(resume_text: str, candidate_name: str) -> bytes:
    """
    Render *resume_text* as a formatted PDF and return the raw bytes.

    Parameters
    ----------
    resume_text : str
        Plain-text resume produced by the LLM.
    candidate_name : str
        Used for logging / metadata only.

    Returns
    -------
    bytes — PDF file content.
    """
    logger.info("Building PDF for: %s", candidate_name)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = _build_styles()
    story = []
    lines = resume_text.split("\n")
    first = True
    second = False  # contact line immediately after name

    for raw in lines:
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 3))
            continue

        upper = line.upper()

        # ── Candidate name (very first non-empty line) ──
        if first:
            story.append(Paragraph(line, styles["name"]))
            first = False
            second = True
            continue

        # ── Contact / email / phone line ──
        if second:
            contact = line.replace("|", "  •  ")
            story.append(Paragraph(contact, styles["contact"]))
            story.append(
                HRFlowable(width="100%", thickness=1.2, color=_ACCENT, spaceAfter=4)
            )
            second = False
            continue

        # ── Section headings ──
        if any(upper == kw or upper.startswith(kw) for kw in _SECTION_KEYWORDS):
            story.append(Spacer(1, 4))
            story.append(Paragraph(upper, styles["section"]))
            story.append(
                HRFlowable(width="100%", thickness=0.5, color=_RULE, spaceAfter=3)
            )
            continue

        # ── Bullet lines ──
        if line.startswith(("•", "-", "*")):
            text = line.lstrip("•-* ").strip()
            story.append(Paragraph(f"–  {text}", styles["bullet"]))
            continue

        # ── Numbered items (projects) ──
        if re.match(r"^\d+\.", line):
            text = line[line.index(".") + 1:].strip()
            story.append(Paragraph(f"–  {text}", styles["bullet"]))
            continue

        # ── General body text ──
        story.append(Paragraph(line, styles["body"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
