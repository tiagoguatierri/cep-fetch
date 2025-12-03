from typing import Dict

from aiohttp import ClientSession

from cep_fetch.core.domain import CepResult
from cep_fetch.core.interfaces import Provider


class BrasilApiProvider(Provider):
    """BrasilAPI provider."""

    @property
    def name(self) -> str:
        return 'brasilapi'

    async def get_cep(self, session: ClientSession, cep: str) -> CepResult:
        """Get CEP information from BrasilAPI."""
        clean_cep = self._clean_cep(cep)
        url = f'https://brasilapi.com.br/api/cep/v1/{clean_cep}'

        async with session.get(url) as response:
            response.raise_for_status()
            data: Dict[str, str] = await response.json()

            return CepResult(
                cep=data.get('cep', ''),
                state=data.get('state', ''),
                city=data.get('city', ''),
                neighborhood=data.get('neighborhood'),
                street=data.get('street'),
                service=self.name,
            )
