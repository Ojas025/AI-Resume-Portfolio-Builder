"""
app.py — Orchestrator entry point.

This file contains ONLY:
  - Streamlit page configuration
  - Top-level layout compositing
  - State management
  - Calling service and UI functions

No business logic, no LLM calls, no CSS here.
"""

import logging
import streamlit as st

import config
from ui.layout import inject_css, render_page_header, render_sidebar, render_empty_state, render_output_tabs
from ui.forms import render_build_form, render_upload_form, render_job_description_input
from utils.validators import validate_form_data, validate_api_key
from services.resume_generator import generate_resume, improve_resume
from services.cover_letter_generator import generate_cover_letter
from services.portfolio_generator import generate_portfolio

logger = logging.getLogger(__name__)

# ── Streamlit page config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _run_generation(form_data: dict, job_description: str) -> bool:
    """
    Call all three generators in sequence, saving results to session state.

    Returns True on success, False on any error.
    """
    resume_text = cover_letter_text = portfolio_html = ""

    with st.spinner("Generating resume..."):
        resume_text, err = generate_resume(
            form_data, job_description=job_description or None
        )
    if err:
        st.error(f"Resume generation failed: {err}")
        if st.button("Retry"):
            st.rerun()
        return False

    with st.spinner("Writing cover letter..."):
        cover_letter_text, err = generate_cover_letter(
            form_data, job_description=job_description or None
        )
    if err:
        st.error(f"Cover letter generation failed: {err}")
        return False

    with st.spinner("Building portfolio page..."):
        portfolio_html, err = generate_portfolio(form_data)
    if err:
        st.error(f"Portfolio generation failed: {err}")
        return False

    # Persist in session state
    st.session_state["resume_text"]       = resume_text
    st.session_state["cover_letter_text"] = cover_letter_text
    st.session_state["portfolio_html"]    = portfolio_html
    st.session_state["candidate_name"]    = form_data["full_name"]
    st.session_state["form_data"]         = form_data
    st.session_state["job_description"]   = job_description
    return True


def _run_upload_improvement(
    raw_text: str,
    parsed_data: dict,
    job_description: str,
) -> bool:
    """Improve an uploaded resume and generate cover letter + portfolio."""
    with st.spinner("Improving resume..."):
        resume_text, err = improve_resume(
            raw_text, job_description=job_description or None
        )
    if err:
        st.error(f"Resume improvement failed: {err}")
        return False

    with st.spinner("Writing cover letter..."):
        cover_letter_text, err = generate_cover_letter(
            parsed_data, job_description=job_description or None
        )
    if err:
        st.error(f"Cover letter failed: {err}")
        return False

    with st.spinner("Building portfolio page..."):
        portfolio_html, err = generate_portfolio(parsed_data)
    if err:
        st.error(f"Portfolio failed: {err}")
        return False

    st.session_state["resume_text"]       = resume_text
    st.session_state["cover_letter_text"] = cover_letter_text
    st.session_state["portfolio_html"]    = portfolio_html
    st.session_state["candidate_name"]    = parsed_data.get("full_name", "Candidate")
    st.session_state["form_data"]         = parsed_data
    st.session_state["job_description"]   = job_description
    return True


def main() -> None:
    inject_css()
    render_page_header()
    render_sidebar()

    # API key guard
    key_err = validate_api_key(config.GEMINI_API_KEY)
    if key_err:
        st.error(key_err)
        st.info("Add your Gemini API key to the sidebar or to a `.env` file as `GEMINI_API_KEY=...`")
        st.stop()

    # ── Main tabs ─────────────────────────────────────────────────────────────
    build_tab, upload_tab, output_tab = st.tabs(
        ["Build Resume", "Upload Resume", "Generated Resume / Cover Letter / Portfolio"]
    )

    # ============================================================
    # TAB 1 — Build Resume (form entry)
    # ============================================================
    with build_tab:
        left, right = st.columns([1, 0.05])   # form only; output is in output_tab
        with left:
            use_example = st.checkbox("Load example data (demo mode)", value=False)
            form_data   = render_build_form(use_example)

            st.markdown("<br>", unsafe_allow_html=True)
            jd_build    = render_job_description_input(key="jd_build")

            st.markdown("<br>", unsafe_allow_html=True)
            generate_btn = st.button(
                "Generate Resume, Cover Letter & Portfolio",
                use_container_width=True,
                type="primary",
            )

            if generate_btn:
                errors = validate_form_data(form_data)
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    ok = _run_generation(form_data, jd_build)
                    if ok:
                        st.success("Generated successfully. View results in the third tab.")

    # ============================================================
    # TAB 2 — Upload Resume
    # ============================================================
    with upload_tab:
        from utils.parser import extract_resume_text, parse_resume_to_structured

        st.markdown(
            """
<p style="color:#6b7280;font-size:0.875rem;margin-bottom:1rem;">
Upload your existing resume to have it improved and tailored.
The AI will rewrite weak bullet points, add measurable outcomes, and optimise for ATS.
</p>
""",
            unsafe_allow_html=True,
        )

        file_bytes, filename, _ = render_upload_form()
        jd_upload = render_job_description_input(key="jd_upload")

        if file_bytes and filename:
            improve_btn = st.button(
                "Improve & Regenerate",
                use_container_width=False,
                type="primary",
            )
            if improve_btn:
                # Step 1: Extract text
                with st.spinner(f"Extracting text from {filename}..."):
                    raw_text, err = extract_resume_text(file_bytes, filename)
                if err:
                    st.error(err)
                    st.stop()

                st.info(f"Extracted {len(raw_text):,} characters from {filename}.")

                # Step 2: Parse into structured data for cover letter / portfolio
                with st.spinner("Parsing resume into structured format..."):
                    parsed_data, err = parse_resume_to_structured(raw_text)
                if err:
                    st.warning(f"Structured parsing had issues: {err}. Proceeding with defaults.")
                    parsed_data = {
                        "full_name": "Candidate",
                        "email": "", "phone": "",
                        "linkedin": "", "github": "",
                        "degree": "", "college": "",
                        "grad_year": 2024, "cgpa": "",
                        "skills": "", "projects": raw_text[:500],
                        "internships": "", "achievements": "",
                        "target_role": "Software Engineer",
                        "experience_level": "Fresher / Entry-level (0–1 yr)",
                    }

                # Step 3: Improve + generate cover letter + portfolio
                ok = _run_upload_improvement(raw_text, parsed_data, jd_upload)
                if ok:
                    st.success("Improvement complete. View results in the third tab.")

    # ============================================================
    # TAB 3 — Output (Resume / Cover Letter / Portfolio)
    # ============================================================
    with output_tab:
        if "resume_text" not in st.session_state:
            render_empty_state()
        else:
            render_output_tabs(
                resume_text=st.session_state["resume_text"],
                cover_letter_text=st.session_state["cover_letter_text"],
                portfolio_html=st.session_state["portfolio_html"],
                candidate_name=st.session_state["candidate_name"],
                form_data=st.session_state.get("form_data", {}),
            )


if __name__ == "__main__":
    main()
