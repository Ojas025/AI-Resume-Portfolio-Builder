# ⬛ AI Resume & Portfolio Builder

> **Generate a polished, ATS-optimised resume, a tailored cover letter, and a personal portfolio page — all in one click, powered by Google Gemini.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?style=flat-square&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)
![Version](https://img.shields.io/badge/Version-2.0.0-8b5cf6?style=flat-square)

---

## ✨ Features

| Feature | Description |
|---|---|
| **Build from Scratch** | Fill in a structured form and generate a complete resume, cover letter, and portfolio in seconds |
| **Upload & Improve** | Upload an existing PDF or DOCX resume and let the AI rewrite weak bullets, remove filler language, and sharpen every claim |
| **JD Tailoring** | Paste a job description to have keywords naturally woven into your resume — no keyword stuffing, no fabrication |
| **ATS Optimisation** | Clean, plain-text output engineered to pass Applicant Tracking Systems with standard section headers and bullet formatting |
| **PDF Export** | Download your generated resume as a formatted PDF with one click |
| **Personal Portfolio Page** | A ready-to-deploy HTML portfolio page generated alongside your resume |
| **Demo Mode** | Load a built-in example candidate to explore all features without entering data |

---

## 🖥️ Application Walkthrough

The app is organised into three tabs:

### Tab 1 — Build Resume
Fill out your personal details, education, skills, projects, internships, and achievements. Optionally paste a job description for tailored output, then click **Generate**.

### Tab 2 — Upload Resume
Upload a `.pdf` or `.docx` file. The AI extracts the text, parses it into structured data, rewrites and improves it, and generates a matching cover letter and portfolio.

### Tab 3 — Generated Output
View and copy your:
- ✅ **Resume** (plain text, ATS-ready)
- ✅ **Cover Letter** (role-specific, non-generic)
- ✅ **Portfolio Page** (live HTML preview + download)
- ✅ **PDF Download** of the resume

---

## 🗂️ Project Structure

```
AI Resume & Portfolio Builder/
│
├── app.py                      # Streamlit entry point & orchestrator
├── main.py                     # Thin launcher (runs app.py via streamlit)
├── config.py                   # Centralised settings & environment variables
├── requirements.txt            # pip dependencies
├── pyproject.toml              # Project metadata (uv / pip-compatible)
├── .env.example                # Environment variable template
│
├── services/
│   ├── llm_service.py          # Single point of contact for all Gemini API calls
│   ├── resume_generator.py     # Resume prompts: standard, JD-tailored, improve
│   ├── cover_letter_generator.py  # Cover letter generation
│   ├── portfolio_generator.py  # HTML portfolio generation
│   └── pdf_service.py          # PDF rendering via ReportLab
│
├── ui/
│   ├── layout.py               # Page header, sidebar, output tabs
│   ├── forms.py                # Build form, upload form, JD input widget
│   └── styles.py               # All custom CSS (injected at runtime)
│
└── utils/
    ├── parser.py               # PDF/DOCX text extraction + LLM-based parser
    └── validators.py           # Form validation & API key guard
```

---

## ⚙️ Architecture Overview

```
User Input (form / upload)
        │
        ▼
   validators.py          ← Validates form fields & API key presence
        │
        ▼
  resume_generator.py  ─┐
  cover_letter_generator ├──► llm_service.py ──► Google Gemini API
  portfolio_generator  ─┘         │
                                   ▼
                            Raw LLM response
                                   │
                   ┌───────────────┼──────────────┐
                   ▼               ▼               ▼
              resume_text   cover_letter_text  portfolio_html
                   │
                   ▼
             pdf_service.py  ──► Downloadable PDF
```

All LLM calls are funnelled through `llm_service.get_llm_response()`. No other module imports `google.generativeai` directly, making it trivial to swap models or providers.

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10** or higher
- A **Google Gemini API key** — [get one here](https://aistudio.google.com/app/apikey)

---

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-resume-portfolio-builder.git
cd "ai-resume-portfolio-builder"
```

### 2. Create and activate a virtual environment

**Using `venv` (standard):**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

**Using `uv` (faster, recommended):**
```bash
uv venv
uv sync
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Copy the example environment file and add your Gemini key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> **Alternatively**, you can paste your API key directly in the app's sidebar at runtime — no restart required.

### 5. Run the application

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 🔧 Configuration

All tuneable settings live in [`config.py`](config.py):

| Variable | Default | Description |
|---|---|---|
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model to use |
| `LLM_TEMPERATURE` | `0.70` | Generation creativity (0.0–1.0) |
| `LLM_TOP_P` | `0.92` | Nucleus sampling threshold |
| `LLM_MAX_TOKENS` | `8192` | Maximum tokens per LLM response |
| `APP_VERSION` | `2.0.0` | Application version string |

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥ 1.32 | Web UI framework |
| `google-generativeai` | ≥ 0.8 | Gemini API client |
| `reportlab` | ≥ 4.1 | PDF generation |
| `python-dotenv` | ≥ 1.0 | `.env` file loading |
| `PyPDF2` | ≥ 3.0 | PDF text extraction |
| `python-docx` | ≥ 1.1 | DOCX text extraction |
| `Pillow` | ≥ 10.0 | Image processing for PDF |

---

## 🧠 How the AI Works

### Prompt Engineering

The resume generator uses a carefully engineered system persona:

> *"You are a senior technical recruiter and professional resume writer with 15 years of experience placing engineers and data scientists at top-tier tech firms."*

**Three generation modes:**

1. **Standard** — Generates a structured, ATS-optimised resume from form data with quantified bullet points.
2. **JD-Tailored** — Extracts keywords from the provided job description and naturally incorporates them without keyword-stuffing or fabricating experience.
3. **Improve** — Takes raw text from an uploaded resume and rewrites passive, vague, or generic statements into sharp, measurable claims while preserving all factual information.

**Hard constraints enforced on every generation:**
- No banned buzzwords ("passionate", "results-driven", "synergy", etc.)
- Every claim is measurable or verifiable
- Plain-text output — no markdown symbols, no emojis
- Standard ATS section order: `PROFESSIONAL SUMMARY / TECHNICAL SKILLS / PROJECTS / INTERNSHIPS & EXPERIENCE / EDUCATION / ACHIEVEMENTS`
- Single A4 page worth of content (~550–650 words)

### Resume Parsing (Upload Mode)

When a file is uploaded, the pipeline runs in three steps:
1. **Text Extraction** — `PyPDF2` (PDF) or `python-docx` (DOCX) extracts raw text
2. **Structured Parsing** — A secondary LLM call parses the raw text into a structured `dict` (name, email, skills, projects, etc.) for use by the cover letter and portfolio generators
3. **Improvement** — A third LLM call rewrites the full resume text using the improvement prompt

---

## 🔒 Security & Privacy

- Your API key is **never stored** by the application — it is held only in memory for the duration of the session.
- Uploaded resume files are processed **in-memory** and are never written to disk.
- The `.env` file is listed in `.gitignore` and will not be committed to version control.

---

## 🐛 Troubleshooting

**`GEMINI_API_KEY is not set`**
→ Ensure your `.env` file exists and contains `GEMINI_API_KEY=...`, or paste the key in the sidebar.

**`PDF appears to be image-based or empty`**
→ Scanned PDFs (images of text) cannot be parsed. Use a text-selectable PDF or a DOCX file instead.

**`Model initialisation failed`**
→ Check that your API key is valid and that you have quota available in [Google AI Studio](https://aistudio.google.com).

**Streamlit import errors in IDE**
→ Ensure your IDE is using the Python interpreter from `.venv`. In VS Code, press `Ctrl+Shift+P` → *Python: Select Interpreter* → choose `.venv`.

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [Google Gemini](https://deepmind.google/technologies/gemini/) — LLM powering all generation
- [Streamlit](https://streamlit.io/) — Rapid web app framework for Python
- [ReportLab](https://www.reportlab.com/) — PDF generation toolkit

---

<p align="center">
  Built with ❤️ using Python & Google Gemini
</p>
