"""
ui/forms.py — Streamlit form rendering for Build Resume and Upload Resume modes.

No LLM calls here — only UI construction and data collection.
Returns structured dicts consumed by app.py.
"""

from typing import Optional
import streamlit as st

import config


def _card(title: str):
    """Render a card-style section header."""
    st.markdown(f'<div class="card-title">{title}</div>', unsafe_allow_html=True)


def render_build_form(use_example: bool) -> dict:
    """
    Render the manual entry form for building a resume from scratch.

    Parameters
    ----------
    use_example : bool
        If True, pre-fill all fields with demo data from config.EXAMPLE_DATA.

    Returns
    -------
    dict — candidate data matching the schema expected by generators.
    """

    def ex(field: str, default="") -> str:
        return str(config.EXAMPLE_DATA.get(field, default)) if use_example else default

    def ex_int(field: str, default: int = 2025) -> int:
        return int(config.EXAMPLE_DATA.get(field, default)) if use_example else default

    # ── Personal Details ────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    _card("Personal Details")

    c1, c2 = st.columns(2)
    full_name = c1.text_input("Full Name *", value=ex("full_name"), placeholder="Jane Doe")
    email     = c2.text_input("Email *", value=ex("email"), placeholder="jane@example.com")

    c3, c4 = st.columns(2)
    phone    = c3.text_input("Phone *", value=ex("phone"), placeholder="+91-XXXXX-XXXXX")
    linkedin = c4.text_input("LinkedIn", value=ex("linkedin"), placeholder="linkedin.com/in/profile")

    github = st.text_input("GitHub", value=ex("github"), placeholder="github.com/username")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Education ───────────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    _card("Education")
    degree  = st.text_input(
        "Degree & Specialisation *", value=ex("degree"),
        placeholder="e.g. B.Tech Computer Science (AI & ML)",
    )
    college = st.text_input(
        "College / University *", value=ex("college"),
        placeholder="e.g. Vellore Institute of Technology",
    )
    e1, e2 = st.columns(2)
    grad_year = e1.number_input(
        "Graduation Year *", min_value=1990, max_value=2035,
        value=ex_int("grad_year"), step=1,
    )
    cgpa = e2.text_input("CGPA / Score", value=ex("cgpa"), placeholder="e.g. 8.7 or 85%")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Technical Skills ─────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    _card("Technical Skills")
    st.caption("Comma-separated list — be specific (e.g. 'PyTorch' not 'ML')")
    skills = st.text_area(
        "Skills *", value=ex("skills"), height=80,
        placeholder="Python, React, PostgreSQL, Docker, AWS Lambda...",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Projects ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    _card("Projects")
    st.caption("Format: Title – what it does / outcome | Tech stack. One per line.")
    projects = st.text_area(
        "Projects *", value=ex("projects"), height=160,
        placeholder=(
            "1. ProjectName – description, scale/outcome | Python, FastAPI\n"
            "2. AnotherProject – ..."
        ),
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Internships ───────────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    _card("Internships / Experience")
    st.caption("Optional")
    internships = st.text_area(
        "Internships", value=ex("internships"), height=90,
        placeholder="Role – Company (Duration): key contribution & measurable outcome",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Achievements ──────────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    _card("Achievements")
    st.caption("Optional — hackathons, awards, open source, competitive programming")
    achievements = st.text_area(
        "Achievements", value=ex("achievements"), height=90,
        placeholder="SIH 2023 National Finalist\nLeetCode 500+ problems, rating 1842",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Target Role ───────────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    _card("Target Role")
    r1, r2 = st.columns([1.4, 1])
    target_role = r1.text_input(
        "Target Role *", value=ex("target_role"),
        placeholder="e.g. ML Engineer, Software Engineer, Data Analyst",
    )
    exp_index = (
        config.EXPERIENCE_LEVELS.index(config.EXAMPLE_DATA["experience_level"])
        if use_example else 0
    )
    experience_level = r2.selectbox(
        "Experience Level", config.EXPERIENCE_LEVELS, index=exp_index,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    return {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "degree": degree,
        "college": college,
        "grad_year": int(grad_year),
        "cgpa": cgpa,
        "skills": skills,
        "projects": projects,
        "internships": internships,
        "achievements": achievements,
        "target_role": target_role,
        "experience_level": experience_level,
    }


def render_upload_form() -> tuple[Optional[bytes], Optional[str], Optional[str]]:
    """
    Render the resume upload widget.

    Returns
    -------
    (file_bytes, filename, job_description)
    All may be None if nothing has been uploaded / entered.
    """
    st.markdown('<div class="card">', unsafe_allow_html=True)
    _card("Upload Existing Resume")
    st.caption("Supported formats: PDF, DOCX — max 5 MB")

    uploaded = st.file_uploader(
        "Choose file",
        type=["pdf", "docx", "doc"],
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    file_bytes: Optional[bytes] = None
    filename: Optional[str]     = None

    if uploaded is not None:
        file_bytes = uploaded.read()
        filename   = uploaded.name
        size_kb    = len(file_bytes) / 1024
        st.success(f"Uploaded: {filename} ({size_kb:.1f} KB)")

    return file_bytes, filename, None  # job_description handled in layout


def render_job_description_input(key: str = "jd") -> str:
    """
    Render the optional job description textarea used by both modes.

    Parameters
    ----------
    key : str
        Unique Streamlit widget key — must differ between call sites.

    Returns
    -------
    str — JD text (empty string if not provided).
    """
    with st.expander("Paste Job Description (optional — improves ATS alignment)"):
        jd = st.text_area(
            "Job Description",
            height=180,
            key=key,
            placeholder=(
                "Paste the full job posting here.\n\n"
                "The AI will extract required skills and keywords, "
                "prioritise your matching experience, and align your resume to this role."
            ),
            label_visibility="collapsed",
        )
    return jd.strip()
