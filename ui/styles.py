"""
ui/styles.py — Custom CSS for the professional black-and-white UI.

Injected into every page via st.markdown(CUSTOM_CSS, unsafe_allow_html=True).
Design inspiration: Notion / Stripe — clean, generous spacing, minimal colour.
"""

CUSTOM_CSS: str = """
<style>
/* ── Fonts ──────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset / base ───────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background: #f9fafb !important;
    color: #111827 !important;
}

[data-testid="stAppViewContainer"] {
    background: #f9fafb !important;
}

/* ── Hide Streamlit chrome ─────────────────────────────────────────────── */
#MainMenu               { visibility: hidden; }
footer                  { visibility: hidden; }
header                  { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f3f4f6; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }

/* ── Page header ────────────────────────────────────────────────────────── */
.page-header {
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 2rem;
}
.page-header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.4px;
    margin: 0 0 0.3rem;
    line-height: 1.2;
}
.page-header p {
    font-size: 0.9rem;
    color: #6b7280;
    margin: 0;
    font-weight: 400;
}

/* ── Section cards ──────────────────────────────────────────────────────── */
.card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.card-title {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #6b7280;
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #f3f4f6;
}

/* ── Inputs ─────────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    color: #111827 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #1d4ed8 !important;
    box-shadow: 0 0 0 3px rgba(29,78,216,0.08) !important;
    outline: none !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label {
    color: #374151 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ── Selectbox ──────────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    color: #111827 !important;
    font-size: 0.875rem !important;
}

/* ── Buttons ────────────────────────────────────────────────────────────── */
[data-testid="stButton"] > button {
    background: #111827 !important;
    color: #ffffff !important;
    border: 1px solid #111827 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.55rem 1.4rem !important;
    letter-spacing: 0.2px !important;
    transition: background 0.15s ease, transform 0.1s ease !important;
    box-shadow: none !important;
}
[data-testid="stButton"] > button:hover {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* ── Download buttons ───────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: border-color 0.15s ease, background 0.15s ease !important;
    width: 100% !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: #1d4ed8 !important;
    color: #1d4ed8 !important;
    background: #eff6ff !important;
}

/* ── Tabs ───────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #ffffff !important;
    border-bottom: 1px solid #e5e7eb !important;
    border-radius: 0 !important;
    padding: 0 !important;
    gap: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #6b7280 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.65rem 1.25rem !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    transition: color 0.15s ease, border-color 0.15s ease !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: transparent !important;
    color: #1d4ed8 !important;
    border-bottom: 2px solid #1d4ed8 !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    padding-top: 1.5rem !important;
    background: transparent !important;
}

/* ── Alerts ─────────────────────────────────────────────────────────────── */
[data-testid="stSuccess"] {
    background: #f0fdf4 !important;
    border: 1px solid #bbf7d0 !important;
    border-radius: 8px !important;
    color: #15803d !important;
    font-size: 0.875rem !important;
}
[data-testid="stError"] {
    background: #fef2f2 !important;
    border: 1px solid #fecaca !important;
    border-radius: 8px !important;
    color: #dc2626 !important;
    font-size: 0.875rem !important;
}
[data-testid="stWarning"] {
    background: #fffbeb !important;
    border: 1px solid #fde68a !important;
    border-radius: 8px !important;
    color: #d97706 !important;
    font-size: 0.875rem !important;
}
[data-testid="stInfo"] {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 8px !important;
    color: #1d4ed8 !important;
    font-size: 0.875rem !important;
}

/* ── File uploader ───────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 1.5px dashed #d1d5db !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    transition: border-color 0.15s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #1d4ed8 !important;
}
[data-testid="stFileUploader"] label {
    color: #374151 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ── Checkbox ───────────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] label {
    color: #374151 !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
}

/* ── Expander ───────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}
[data-testid="stExpander"] summary {
    color: #374151 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* ── Resume / letter preview ─────────────────────────────────────────────── */
.doc-preview {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 2.25rem 2.75rem;
    font-family: 'Inter', sans-serif;
    color: #111827;
    line-height: 1.75;
    font-size: 0.875rem;
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.doc-preview .doc-name {
    font-size: 1.4rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.15rem;
}
.doc-preview .doc-contact {
    font-size: 0.78rem;
    color: #6b7280;
    margin-bottom: 0.75rem;
}
.doc-preview .doc-section {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #1d4ed8;
    margin: 1.25rem 0 0.4rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid #e5e7eb;
}
.doc-preview .doc-bullet {
    color: #374151;
    padding-left: 1rem;
    text-indent: -0.8rem;
    margin-bottom: 0.25rem;
}

/* ── Empty state ────────────────────────────────────────────────────────── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 420px;
    background: #ffffff;
    border: 1.5px dashed #e5e7eb;
    border-radius: 12px;
    color: #9ca3af;
    text-align: center;
    padding: 2rem;
}
.empty-state .empty-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
    opacity: 0.4;
}
.empty-state .empty-title {
    font-size: 0.95rem;
    font-weight: 500;
    color: #6b7280;
    margin-bottom: 0.3rem;
}
.empty-state .empty-sub {
    font-size: 0.8rem;
    color: #9ca3af;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e5e7eb !important;
}
[data-testid="stSidebar"] h3 {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
    color: #6b7280 !important;
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid #e5e7eb !important;
    margin: 1.25rem 0 !important;
}

/* ── Spinner ────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div {
    border-top-color: #1d4ed8 !important;
}
</style>
"""
