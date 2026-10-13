"""A deliberately limited, offline-only chat placeholder for legacy demonstrations."""
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name="TBscore II"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return "Offline mock response only; no clinical or scientific verification was performed."


class LLMFactory:
    @staticmethod
    def create(provider="mock", system_name="TBscore II"):
        if str(provider).lower() in ("mock", "deterministic", "test"):
            return MockLLM(system_name)
        raise ValueError("Only offline mock mode is implemented; external model providers are unavailable.")
