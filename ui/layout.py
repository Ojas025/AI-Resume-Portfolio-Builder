"""
ui/layout.py — Reusable layout helpers (header, sidebar, output panels).

No LLM calls and no business logic — only rendering.
"""

import logging
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

import config
from ui.styles import CUSTOM_CSS

logger = logging.getLogger(__name__)

# ── Section keywords for HTML resume preview ───────────────────────────────────
_SECTION_KEYWORDS = frozenset({
    "PROFESSIONAL SUMMARY", "SUMMARY",
    "TECHNICAL SKILLS", "SKILLS",
    "PROJECTS",
    "INTERNSHIPS & EXPERIENCE", "INTERNSHIPS", "EXPERIENCE",
    "EDUCATION",
    "ACHIEVEMENTS", "CERTIFICATIONS",
})


def inject_css() -> None:
    """Inject the global custom CSS into the page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_page_header() -> None:
    """Render the top page header."""
    st.markdown(
        f"""
        <div class="page-header">
            <h1>{config.APP_TITLE}</h1>
            <p>Generate ATS-optimised resumes, tailored cover letters, and portfolio pages in seconds.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Render sidebar with API key override and tips."""
    with st.sidebar:
        st.markdown("### Configuration")
        manual_key = st.text_input(
            "Gemini API Key (override)",
            type="password",
            placeholder="AIza...",
            help="Leave blank to use GEMINI_API_KEY from .env",
        )
        if manual_key and manual_key.strip():
            import os
            os.environ["GEMINI_API_KEY"] = manual_key.strip()
            config.GEMINI_API_KEY = manual_key.strip()
            st.success("API key set")

        st.markdown("---")
        st.markdown("### Model")
        fallback_text = ", ".join(config.GEMINI_FALLBACK_MODELS) or "None"
        st.markdown(
            (
                "<small style='color:#6b7280'>"
                f"Primary: <code>{config.GEMINI_MODEL}</code><br>"
                f"Fallbacks: <code>{fallback_text}</code>"
                "</small>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("### Tips")
        st.markdown(
            """
<small style='color:#6b7280'>
- Include project outcomes with numbers<br>
- Use the JD field for best ATS alignment<br>
- Upload your existing resume to improve it<br>
- Click <b>Regenerate</b> if the result needs work
</small>
""",
            unsafe_allow_html=True,
        )


def render_empty_state() -> None:
    """Render the placeholder shown before any content is generated."""
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">&#9635;</div>
            <div class="empty-title">No content generated yet</div>
            <div class="empty-sub">Fill the form and click Generate</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _resume_to_html(text: str) -> str:
    """
    Convert plain-text LLM resume output to a styled HTML preview.

    The first non-blank line → candidate name
    The second non-blank line → contact
    Lines matching SECTION_KEYWORDS → blue section headers
    Lines starting with –/•/- → bullet items
    Everything else → body paragraph
    """
    import re
    lines = text.split("\n")
    parts: list[str] = ['<div class="doc-preview">']
    first = True
    second = False

    for raw in lines:
        line = raw.strip()
        if not line:
            parts.append("<br>")
            continue

        upper = line.upper()

        if first:
            parts.append(f'<div class="doc-name">{line}</div>')
            first = False
            second = True
            continue

        if second:
            contact = line.replace("|", " &bull; ")
            parts.append(f'<div class="doc-contact">{contact}</div>')
            parts.append('<hr style="border:none;border-top:1px solid #e5e7eb;margin:0.5rem 0 0.75rem;">')
            second = False
            continue

        if any(upper == kw or upper.startswith(kw) for kw in _SECTION_KEYWORDS):
            parts.append(f'<div class="doc-section">{upper}</div>')
            continue

        if line.startswith(("•", "-", "–", "*")):
            body = line.lstrip("•-–* ").strip()
            parts.append(f'<div class="doc-bullet">&#8212;&nbsp;&nbsp;{body}</div>')
            continue

        if re.match(r"^\d+\.", line):
            body = line.split(".", 1)[-1].strip()
            parts.append(f'<div class="doc-bullet">&#8212;&nbsp;&nbsp;{body}</div>')
            continue

        parts.append(f'<p style="margin:0 0 0.25rem;color:#374151;font-size:0.875rem;">{line}</p>')

    parts.append("</div>")
    return "\n".join(parts)


def render_output_tabs(
    resume_text: str,
    cover_letter_text: str,
    portfolio_html: str,
    candidate_name: str,
    form_data: dict,
) -> None:
    """
    Render the Generated Resume / Cover Letter / Portfolio output tabs.

    Parameters
    ----------
    resume_text : str
    cover_letter_text : str
    portfolio_html : str
    candidate_name : str
    form_data : dict — needed for the inline regenerate buttons
    """
    from services.resume_generator import generate_resume
    from services.cover_letter_generator import generate_cover_letter
    from services.portfolio_generator import generate_portfolio
    from services.pdf_service import create_pdf

    tab_resume, tab_cover, tab_portfolio = st.tabs(
        ["Generated Resume", "Cover Letter", "Portfolio"]
    )

    safe_name = candidate_name.replace(" ", "_")
    jd = st.session_state.get("job_description", "")

    # ── Resume tab ────────────────────────────────────────────────────────────
    with tab_resume:
        st.markdown(_resume_to_html(resume_text), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        dl_col, regen_col, raw_col = st.columns([1.2, 1.2, 1])

        with dl_col:
            try:
                pdf_bytes = create_pdf(resume_text, candidate_name)
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"{safe_name}_Resume.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"PDF error: {e}")

        with regen_col:
            if st.button("Regenerate Resume", use_container_width=True):
                with st.spinner("Regenerating..."):
                    new_text, err = generate_resume(form_data, job_description=jd or None)
                if err:
                    st.error(err)
                else:
                    st.session_state["resume_text"] = new_text
                    st.rerun()

        with raw_col:
            with st.expander("Copy text"):
                st.code(resume_text, language="")

    # ── Cover Letter tab ───────────────────────────────────────────────────────
    with tab_cover:
        cl_html = _resume_to_html(cover_letter_text)
        st.markdown(cl_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        cl_dl, cl_regen, cl_raw = st.columns([1.2, 1.2, 1])

        with cl_dl:
            st.download_button(
                label="Download (.txt)",
                data=cover_letter_text.encode(),
                file_name=f"{safe_name}_CoverLetter.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with cl_regen:
            if st.button("Regenerate Cover Letter", use_container_width=True):
                with st.spinner("Regenerating..."):
                    new_cl, err = generate_cover_letter(form_data, job_description=jd or None)
                if err:
                    st.error(err)
                else:
                    st.session_state["cover_letter_text"] = new_cl
                    st.rerun()

        with cl_raw:
            with st.expander("Copy text"):
                st.code(cover_letter_text, language="")

    # ── Portfolio tab ──────────────────────────────────────────────────────────
    with tab_portfolio:
        components.html(portfolio_html, height=700, scrolling=True)
        st.markdown("<br>", unsafe_allow_html=True)

        pt_dl, pt_regen = st.columns(2)

        with pt_dl:
            st.download_button(
                label="Download HTML",
                data=portfolio_html.encode(),
                file_name=f"{safe_name}_Portfolio.html",
                mime="text/html",
                use_container_width=True,
            )

        with pt_regen:
            if st.button("Regenerate Portfolio", use_container_width=True):
                with st.spinner("Regenerating..."):
                    new_p, err = generate_portfolio(form_data)
                if err:
                    st.error(err)
                else:
                    st.session_state["portfolio_html"] = new_p
                    st.rerun()
