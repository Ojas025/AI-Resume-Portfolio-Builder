"""
utils/parser.py — Resume text extraction from uploaded files.

Supports:
  - PDF  → PyPDF2
  - DOCX → python-docx
  - LLM-based structured parsing of extracted text
"""

import logging
from typing import Optional
from io import BytesIO

logger = logging.getLogger(__name__)

# ── PDF extraction ────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, Optional[str]]:
    """
    Extract plain text from a PDF file.

    Parameters
    ----------
    file_bytes : bytes
        Raw bytes of the uploaded PDF.

    Returns
    -------
    (text, error)
    """
    try:
        import PyPDF2  # type: ignore
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if not text:
            return "", "PDF appears to be image-based or empty — no text could be extracted."
        logger.info("Extracted %d chars from PDF (%d pages)", len(text), len(pages))
        return text, None
    except ImportError:
        return "", "PyPDF2 is not installed. Run: pip install PyPDF2"
    except Exception as exc:
        logger.exception("PDF extraction failed")
        return "", f"PDF extraction error: {exc}"


# ── DOCX extraction ───────────────────────────────────────────────────────────

def extract_text_from_docx(file_bytes: bytes) -> tuple[str, Optional[str]]:
    """
    Extract plain text from a DOCX file.

    Parameters
    ----------
    file_bytes : bytes
        Raw bytes of the uploaded DOCX.

    Returns
    -------
    (text, error)
    """
    try:
        from docx import Document  # type: ignore
        doc = Document(BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs).strip()
        if not text:
            return "", "DOCX appears to be empty — no text could be extracted."
        logger.info("Extracted %d chars from DOCX (%d paragraphs)", len(text), len(paragraphs))
        return text, None
    except ImportError:
        return "", "python-docx is not installed. Run: pip install python-docx"
    except Exception as exc:
        logger.exception("DOCX extraction failed")
        return "", f"DOCX extraction error: {exc}"


# ── Dispatcher ────────────────────────────────────────────────────────────────

def extract_resume_text(file_bytes: bytes, filename: str) -> tuple[str, Optional[str]]:
    """
    Route to the correct extractor based on file extension.

    Parameters
    ----------
    file_bytes : bytes
    filename : str

    Returns
    -------
    (text, error)
    """
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        return extract_text_from_docx(file_bytes)
    else:
        return "", f"Unsupported file type '.{ext}'. Please upload a PDF or DOCX."


# ── LLM-assisted structured parser ───────────────────────────────────────────

def parse_resume_to_structured(raw_text: str) -> tuple[dict, Optional[str]]:
    """
    Use the LLM to extract structured fields from a raw resume text.

    Returns a partial dict compatible with the form data schema
    (missing fields will be empty strings).

    Parameters
    ----------
    raw_text : str
        Plain text of the uploaded resume.

    Returns
    -------
    (data_dict, error)
    """
    from services.llm_service import get_llm_response

    prompt = f"""Extract structured information from the resume below.
Return a Python dictionary literal (no backticks, no markdown) with these exact keys:
  full_name, email, phone, linkedin, github,
  degree, college, grad_year (int), cgpa,
  skills, projects, internships, achievements, target_role

Rules:
- grad_year must be an integer (e.g. 2024). Use 0 if unknown.
- For skills: comma-separated string
- For projects: numbered list as a single string
- For linkedin/github: just the URL or profile path, no label
- If a field is not found, use an empty string "" (or 0 for grad_year)
- Return ONLY the dict literal starting with {{ and ending with }}

Resume text:
---
{raw_text[:4000]}
---
"""
    text, err = get_llm_response(prompt)
    if err:
        return {}, err

    # Safely evaluate the returned dict literal
    try:
        # Strip markdown code fences if model adds them
        clean = text.strip().lstrip("```python").lstrip("```").rstrip("```").strip()
        data: dict = eval(clean, {"__builtins__": {}})  # noqa: S307
        # Ensure grad_year is int
        data["grad_year"] = int(data.get("grad_year") or 0) or 2024
        # Fill missing keys with defaults
        for key in ["full_name", "email", "phone", "linkedin", "github",
                    "degree", "college", "cgpa", "skills", "projects",
                    "internships", "achievements", "target_role"]:
            data.setdefault(key, "")
        data.setdefault("experience_level", "Fresher / Entry-level (0–1 yr)")
        logger.info("Parsed resume into structured dict: name=%s", data.get("full_name"))
        return data, None
    except Exception as exc:
        logger.exception("Failed to parse LLM dict output")
        return {}, f"Could not parse LLM response into structured data: {exc}"
