import unittest
from types import SimpleNamespace
from unittest.mock import patch

from services import llm_service


class _FakeResponse:
    def __init__(self, text=None, parts=None, text_error=None):
        self._text = text
        self._text_error = text_error
        self.candidates = []
        if parts:
            self.candidates = [
                SimpleNamespace(
                    content=SimpleNamespace(
                        parts=[SimpleNamespace(text=value) for value in parts]
                    )
                )
            ]

    @property
    def text(self):
        if self._text_error:
            raise self._text_error
        return self._text


class _FakeModel:
    def __init__(self, model_name, responses, failures):
        self.model_name = model_name
        self._responses = responses
        self._failures = failures

    def generate_content(self, prompt: str):
        if self.model_name in self._failures:
            raise self._failures[self.model_name]
        return self._responses[self.model_name]


class LlmServiceTests(unittest.TestCase):
    def _model_factory(self, responses, failures):
        def factory(*, model_name, generation_config):
            return _FakeModel(model_name, responses, failures)

        return factory

    def test_primary_model_success(self):
        responses = {"gemini-2.5-flash": _FakeResponse(text="```html\nHello\n```")}

        with patch.object(llm_service.config, "GEMINI_API_KEY", "test-key"), \
             patch.object(llm_service.config, "GEMINI_MODEL", "gemini-2.5-flash"), \
             patch.object(llm_service.config, "GEMINI_FALLBACK_MODELS", ["gemini-2.5-flash-lite"]), \
             patch.object(llm_service.genai, "configure"), \
             patch.object(llm_service.genai, "GenerationConfig", side_effect=lambda **kwargs: kwargs), \
             patch.object(
                 llm_service.genai,
                 "GenerativeModel",
                 side_effect=self._model_factory(responses, {}),
             ):
            text, err = llm_service.get_llm_response("test prompt")

        self.assertIsNone(err)
        self.assertEqual(text, "Hello")

    def test_falls_back_when_primary_generation_fails(self):
        responses = {"gemini-2.5-flash-lite": _FakeResponse(text="Fallback works")}
        failures = {"gemini-2.5-flash": RuntimeError("429 model unavailable")}

        with patch.object(llm_service.config, "GEMINI_API_KEY", "test-key"), \
             patch.object(llm_service.config, "GEMINI_MODEL", "gemini-2.5-flash"), \
             patch.object(llm_service.config, "GEMINI_FALLBACK_MODELS", ["gemini-2.5-flash-lite"]), \
             patch.object(llm_service.genai, "configure"), \
             patch.object(llm_service.genai, "GenerationConfig", side_effect=lambda **kwargs: kwargs), \
             patch.object(
                 llm_service.genai,
                 "GenerativeModel",
                 side_effect=self._model_factory(responses, failures),
             ):
            text, err = llm_service.get_llm_response("test prompt")

        self.assertIsNone(err)
        self.assertEqual(text, "Fallback works")

    def test_manual_candidate_parsing_when_response_text_is_unavailable(self):
        responses = {
            "gemini-2.5-flash": _FakeResponse(
                parts=["Line one", "Line two"],
                text_error=ValueError("No text accessor available"),
            )
        }

        with patch.object(llm_service.config, "GEMINI_API_KEY", "test-key"), \
             patch.object(llm_service.config, "GEMINI_MODEL", "gemini-2.5-flash"), \
             patch.object(llm_service.config, "GEMINI_FALLBACK_MODELS", []), \
             patch.object(llm_service.genai, "configure"), \
             patch.object(llm_service.genai, "GenerationConfig", side_effect=lambda **kwargs: kwargs), \
             patch.object(
                 llm_service.genai,
                 "GenerativeModel",
                 side_effect=self._model_factory(responses, {}),
             ):
            text, err = llm_service.get_llm_response("test prompt")

        self.assertIsNone(err)
        self.assertEqual(text, "Line one\nLine two")


if __name__ == "__main__":
    unittest.main()
