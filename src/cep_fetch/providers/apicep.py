from typing import Dict

from aiohttp import ClientSession

from cep_fetch.core.domain import CepResult
from cep_fetch.core.interfaces import Provider


class ApiCepProvider(Provider):
    """ApiCEP provider."""

    @property
    def name(self) -> str:
        return 'apicep'

    async def get_cep(self, session: ClientSession, cep: str) -> CepResult:
        """Get CEP information from ApiCEP."""
        clean_cep = self._clean_cep(cep)
        url = f'https://cdn.apicep.com/file/apicep/{clean_cep}.json'

        async with session.get(url) as response:
            response.raise_for_status()
            data: Dict[str, str] = await response.json()

            return CepResult(
                cep=data.get('code', ''),
                state=data.get('state', ''),
                city=data.get('city', ''),
                neighborhood=data.get('district'),
                street=data.get('address'),
                service=self.name,
            )
