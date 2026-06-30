from __future__ import annotations

import logging
from pathlib import Path

from backend.core.config import get_settings

logger = logging.getLogger(__name__)


class LlamaCppEngine:
    def __init__(self, model_path: str | Path | None = None) -> None:
        self.settings = get_settings()
        self.model_path = Path(model_path or self.settings.paths.llm_model_path)
        self._llm = None

    def available(self) -> bool:
        return self.model_path.exists()

    def _load(self):
        if self._llm is None:
            if not self.model_path.exists():
                self._llm = False
            else:
                try:
                    from llama_cpp import Llama

                    self._llm = Llama(
                        model_path=str(self.model_path),
                        n_ctx=self.settings.llm.context_window,
                        n_threads=None,
                        verbose=False,
                    )
                except Exception:
                    logger.exception("Local LLM could not be loaded from %s", self.model_path)
                    self._llm = False
        return self._llm

    def generate(self, prompt: str) -> str:
        llm = self._load()
        if not llm:
            return ""
        result = llm(
            prompt,
            max_tokens=self.settings.llm.max_tokens,
            temperature=self.settings.llm.temperature,
            stop=["\n\nQuestion:", "\n\nContext:"],
        )
        return result["choices"][0]["text"].strip()
