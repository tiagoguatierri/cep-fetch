from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CepResult:
    """Unified response object."""

    cep: str
    state: str
    city: str
    neighborhood: Optional[str]
    street: Optional[str]
    service: str  # Which provider returned the response (ex: 'viacep')
