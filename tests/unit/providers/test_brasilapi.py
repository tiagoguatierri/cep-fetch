"""Tests for BrasilAPI provider."""

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from cep_fetch.core.domain import CepResult
from cep_fetch.providers import BrasilApiProvider


class TestBrasilApiProvider:
    """Tests for BrasilAPI provider."""

    def test_provider_name(self):
        """Test that provider name is correct."""
        provider = BrasilApiProvider()
        assert provider.name == 'brasilapi'

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
        provider = BrasilApiProvider()
        assert provider._clean_cep(cep) == clean_cep

    async def test_get_cep_success(self):
        """Test successful CEP fetch from BrasilAPI."""
        provider = BrasilApiProvider()
        cep = '01001000'

        mock_response = {
            'cep': '01001000',
            'state': 'SP',
            'city': 'São Paulo',
            'neighborhood': 'Sé',
            'street': 'Praça da Sé',
        }

        with aioresponses() as mocked:
            mocked.get(
                f'https://brasilapi.com.br/api/cep/v1/{cep}',
                payload=mock_response,
                status=200,
            )

            async with ClientSession() as session:
                result = await provider.get_cep(session, cep)

                assert isinstance(result, CepResult)
                assert result.cep == '01001000'
                assert result.state == 'SP'
                assert result.city == 'São Paulo'
                assert result.neighborhood == 'Sé'
                assert result.street == 'Praça da Sé'
                assert result.service == 'brasilapi'

    async def test_get_cep_not_found(self):
        """Test CEP not found error from BrasilAPI."""
        provider = BrasilApiProvider()
        cep = '99999999'

        with aioresponses() as mocked:
            mocked.get(
                f'https://brasilapi.com.br/api/cep/v1/{cep}',
                status=404,
            )

            async with ClientSession() as session:
                with pytest.raises(Exception):
                    await provider.get_cep(session, cep)
