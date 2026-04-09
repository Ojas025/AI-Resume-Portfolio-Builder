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


def _generation_config() -> genai.GenerationConfig:
    """Build the shared generation config for all model attempts."""
    return genai.GenerationConfig(
        temperature=config.LLM_TEMPERATURE,
        top_p=config.LLM_TOP_P,
        max_output_tokens=config.LLM_MAX_TOKENS,
    )


def _build_model(model_name: str) -> tuple[Optional[genai.GenerativeModel], Optional[str]]:
    """Configure and return a GenerativeModel instance for *model_name*."""
    api_key = config.GEMINI_API_KEY
    if not api_key:
        return None, (
            "GEMINI_API_KEY is not set. "
            "Add it to your .env file or paste it in the sidebar."
        )
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=_generation_config(),
        )
        return model, None
    except Exception as exc:
        logger.exception("Failed to initialise Gemini model %s", model_name)
        return None, f"Model initialisation failed for {model_name}: {exc}"


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


def _extract_text(response) -> str:
    """
    Extract text from a Gemini response.

    `response.text` can itself raise when the SDK receives a blocked/empty
    candidate, so fall back to walking the candidate content manually.
    """
    try:
        text = response.text
        if text:
            return _strip_code_fences(text)
    except Exception:
        logger.debug("Falling back to manual response parsing", exc_info=True)

    parts: list[str] = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            value = getattr(part, "text", None)
            if value:
                parts.append(value)

    text = "\n".join(parts).strip()
    if not text:
        raise ValueError("Gemini returned no text content")
    return _strip_code_fences(text)


def _candidate_models() -> list[str]:
    """Return the ordered list of models to try."""
    models = [config.GEMINI_MODEL, *getattr(config, "GEMINI_FALLBACK_MODELS", [])]
    seen: set[str] = set()
    ordered: list[str] = []
    for model in models:
        if model and model not in seen:
            ordered.append(model)
            seen.add(model)
    return ordered


def get_llm_response(prompt: str) -> tuple[str, Optional[str]]:
    """
    Send *prompt* to the configured Gemini model list.

    Parameters
    ----------
    prompt : str
        The full prompt text to send (system + user combined).

    Returns
    -------
    (text, error) — on success *error* is None; on failure *text* is empty.
    """
    errors: list[str] = []

    for model_name in _candidate_models():
        model, err = _build_model(model_name)
        if err:
            errors.append(err)
            continue

        try:
            logger.info("Sending request to %s (len=%d chars)", model_name, len(prompt))
            response = model.generate_content(prompt)
            text = _extract_text(response)
            logger.info("Received response from %s (%d chars)", model_name, len(text))
            return text, None
        except Exception as exc:
            logger.exception("LLM call failed for %s", model_name)
            errors.append(f"{model_name}: {exc}")

    if not errors:
        return "", "LLM request failed: no Gemini models configured"

    return "", "LLM request failed. Attempts: " + " | ".join(errors)
