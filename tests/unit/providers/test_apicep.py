"""Tests for ApiCEP provider."""

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from cep_fetch.core.domain import CepResult
from cep_fetch.providers import ApiCepProvider


class TestApiCepProvider:
    """Tests for ApiCEP provider."""

    def test_provider_name(self):
        """Test that provider name is correct."""
        provider = ApiCepProvider()
        assert provider.name == 'apicep'

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
        provider = ApiCepProvider()
        assert provider._clean_cep(cep) == clean_cep

    async def test_get_cep_success(self):
        """Test successful CEP fetch from ApiCEP."""
        provider = ApiCepProvider()
        cep = '01001000'

        mock_response = {
            'code': '01001-000',
            'state': 'SP',
            'city': 'São Paulo',
            'district': 'Sé',
            'address': 'Praça da Sé',
        }

        with aioresponses() as mocked:
            mocked.get(
                f'https://cdn.apicep.com/file/apicep/{cep}.json',
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
                assert result.service == 'apicep'

    async def test_get_cep_not_found(self):
        """Test CEP not found error from ApiCEP."""
        provider = ApiCepProvider()
        cep = '99999999'

        with aioresponses() as mocked:
            mocked.get(
                f'https://cdn.apicep.com/file/apicep/{cep}.json',
                status=404,
            )

            async with ClientSession() as session:
                with pytest.raises(Exception):
                    await provider.get_cep(session, cep)
