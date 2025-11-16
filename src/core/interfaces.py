from abc import ABC, abstractmethod

from aiohttp import ClientSession

from .domain import CepResult


class Provider(ABC):
    """Base abstract class for all providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Service identifier (ex: 'viacep')."""

    @abstractmethod
    async def get_cep(self, session: ClientSession, cep: str) -> CepResult:
        """
        Must search the CEP and return a normalized CepResult.
        Must raise exceptions if it fails, so the orchestrator can handle it.
        """

    def _clean_cep(self, cep: str) -> str:
        """Helper to clean the CEP (only numbers)."""
        return ''.join(filter(str.isdigit, cep))
