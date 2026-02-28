"""
services/llm_service.py — Single point of contact for all LLM calls.

All Gemini API interaction is isolated here. Other modules call
`get_llm_response()` and never import google.generativeai directly.
"""

import logging
from typing import Optional

import google.generativeai as genai

import config

logger = logging.getLogger(__name__)


def _build_model() -> tuple[Optional[genai.GenerativeModel], Optional[str]]:
    """
    Configure and return a GenerativeModel instance.

    Returns
    -------
    (model, error_message) — exactly one of the two will be non-None.
    """
    api_key = config.GEMINI_API_KEY
    if not api_key:
        return None, (
            "GEMINI_API_KEY is not set. "
            "Add it to your .env file or paste it in the sidebar."
        )
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            generation_config=genai.GenerationConfig(
                temperature=config.LLM_TEMPERATURE,
                top_p=config.LLM_TOP_P,
                max_output_tokens=config.LLM_MAX_TOKENS,
            ),
        )
        return model, None
    except Exception as exc:
        logger.exception("Failed to initialise Gemini model")
        return None, f"Model initialisation failed: {exc}"


def _strip_code_fences(text: str) -> str:
    """
    Remove markdown code fences that Gemini sometimes adds despite instructions.

    Handles patterns like:
        ```html\\n...\\n```
        ```python\\n...\\n```
        ```\\n...\\n```
    """
    import re
    # Remove opening fence with optional language tag
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
    # Remove closing fence
    text = re.sub(r"\n?```$", "", text.strip())
    return text.strip()


def get_llm_response(prompt: str) -> tuple[str, Optional[str]]:
    """
    Send *prompt* to the configured Gemini model.

    Parameters
    ----------
    prompt : str
        The full prompt text to send (system + user combined).

    Returns
    -------
    (text, error) — on success *error* is None; on failure *text* is empty.
    """
    model, err = _build_model()
    if err:
        return "", err

    try:
        logger.info("Sending request to %s (len=%d chars)", config.GEMINI_MODEL, len(prompt))
        response = model.generate_content(prompt)
        text = _strip_code_fences(response.text)
        logger.info("Received response (%d chars)", len(text))
        return text, None
    except Exception as exc:
        logger.exception("LLM call failed")
        return "", f"LLM request failed: {exc}"

