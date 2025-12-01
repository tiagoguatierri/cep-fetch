from typing import Dict

from aiohttp import ClientSession

from cep_fetch.core.domain import CepResult
from cep_fetch.core.interfaces import Provider


class OpenCepProvider(Provider):
    """OpenCEP provider."""

    @property
    def name(self) -> str:
        return 'opencep'

    async def get_cep(self, session: ClientSession, cep: str) -> CepResult:
        """Get CEP information from OpenCEP."""
        clean_cep = self._clean_cep(cep)
        url = f'https://opencep.com/v1/{clean_cep}'

        async with session.get(url) as response:
            response.raise_for_status()
            data: Dict[str, str] = await response.json()

            return CepResult(
                cep=data.get('cep', ''),
                state=data.get('uf', ''),
                city=data.get('localidade', ''),
                neighborhood=data.get('bairro'),
                street=data.get('logradouro'),
                service=self.name,
            )
