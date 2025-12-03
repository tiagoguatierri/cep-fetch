from typing import Dict

from aiohttp import ClientSession

from cep_fetch.core.domain import CepResult
from cep_fetch.core.interfaces import Provider


class ViaCepProvider(Provider):
    """ViaCEP provider."""

    @property
    def name(self) -> str:
        return 'viacep'

    async def get_cep(self, session: ClientSession, cep: str) -> CepResult:
        """Get CEP information from ViaCEP."""
        clean_cep = self._clean_cep(cep)
        url = f'https://viacep.com.br/ws/{clean_cep}/json/'

        async with session.get(url) as response:
            response.raise_for_status()
            data: Dict[str, str] = await response.json()

            if 'erro' in data:
                raise ValueError(f'CEP {cep} não encontrado no ViaCEP')

            return CepResult(
                cep=data.get('cep', ''),
                state=data.get('uf', ''),
                city=data.get('localidade', ''),
                neighborhood=data.get('bairro'),
                street=data.get('logradouro'),
                service=self.name,
            )
