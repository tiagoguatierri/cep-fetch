"""Tests for ViaCEP provider."""

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from cep_fetch.core.domain import CepResult
from cep_fetch.providers import ViaCepProvider


class TestViaCepProvider:
    """Tests for ViaCEP provider."""

    def test_provider_name(self):
        """Test that provider name is correct."""
        provider = ViaCepProvider()
        assert provider.name == 'viacep'

    @pytest.mark.parametrize(
        'cep,clean_cep',
        [
            ('01001-000', '01001000'),
            ('01001000', '01001000'),
            ('01.001-000', '01001000'),
        ],
    )
    def test_clean_cep(self, cep: str, clean_cep: str):
        """Test CEP cleaning with different formats."""
        provider = ViaCepProvider()
        assert provider._clean_cep(cep) == clean_cep

    async def test_get_cep_success(self):
        """Test successful CEP fetch from ViaCEP."""
        provider = ViaCepProvider()
        cep = '01001000'

        mock_response = {
            'cep': '01001-000',
            'uf': 'SP',
            'localidade': 'São Paulo',
            'bairro': 'Sé',
            'logradouro': 'Praça da Sé',
        }

        with aioresponses() as mocked:
            mocked.get(
                f'https://viacep.com.br/ws/{cep}/json/',
                payload=mock_response,
                status=200,
            )

            async with ClientSession() as session:
                result = await provider.get_cep(session, cep)

                assert isinstance(result, CepResult)
                assert result.cep == '01001-000'
                assert result.state == 'SP'
                assert result.city == 'São Paulo'
                assert result.neighborhood == 'Sé'
                assert result.street == 'Praça da Sé'
                assert result.service == 'viacep'

    async def test_get_cep_not_found(self):
        """Test CEP not found error from ViaCEP."""
        provider = ViaCepProvider()
        cep = '99999999'

        mock_response = {'erro': True}

        with aioresponses() as mocked:
            mocked.get(
                f'https://viacep.com.br/ws/{cep}/json/',
                payload=mock_response,
                status=200,
            )

            async with ClientSession() as session:
                with pytest.raises(ValueError, match='não encontrado'):
                    await provider.get_cep(session, cep)

    async def test_get_cep_http_error(self):
        """Test HTTP error handling from ViaCEP."""
        provider = ViaCepProvider()
        cep = '01001000'

        with aioresponses() as mocked:
            mocked.get(
                f'https://viacep.com.br/ws/{cep}/json/',
                status=500,
            )

            async with ClientSession() as session:
                with pytest.raises(Exception):
                    await provider.get_cep(session, cep)
