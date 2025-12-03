"""Integration tests for CepFetch with real providers."""

import pytest
from aioresponses import aioresponses

from cep_fetch.cep_fetch import CepFetch
from cep_fetch.providers import ApiCepProvider, BrasilApiProvider, OpenCepProvider, ViaCepProvider


class TestCepFetchWithRealProviders:
    """Integration tests using actual provider implementations."""

    async def test_search_with_viacep_responding_fastest(self):
        """Test that ViaCEP result is returned when it responds first."""
        cep = '01001000'

        viacep_response = {
            'cep': '01001-000',
            'uf': 'SP',
            'localidade': 'São Paulo',
            'bairro': 'Sé',
            'logradouro': 'Praça da Sé',
        }

        with aioresponses() as mocked:
            # ViaCEP responds immediately
            mocked.get(
                f'https://viacep.com.br/ws/{cep}/json/',
                payload=viacep_response,
                status=200,
            )

            # Other providers respond with delay (simulated by not being called)
            cep_fetch = CepFetch(providers=[ViaCepProvider()])
            result = await cep_fetch.search(cep)

            assert result.service == 'viacep'
            assert result.cep == '01001-000'
            assert result.state == 'SP'
            assert result.city == 'São Paulo'

    async def test_search_with_brasilapi_responding_fastest(self):
        """Test that BrasilAPI result is returned when it responds first."""
        cep = '01001000'

        brasilapi_response = {
            'cep': '01001000',
            'state': 'SP',
            'city': 'São Paulo',
            'neighborhood': 'Sé',
            'street': 'Praça da Sé',
        }

        with aioresponses() as mocked:
            mocked.get(
                f'https://brasilapi.com.br/api/cep/v1/{cep}',
                payload=brasilapi_response,
                status=200,
            )

            cep_fetch = CepFetch(providers=[BrasilApiProvider()])
            result = await cep_fetch.search(cep)

            assert result.service == 'brasilapi'
            assert result.cep == '01001000'
            assert result.state == 'SP'

    async def test_search_fallback_when_first_provider_fails(self):
        """Test fallback to other providers when first one fails."""
        cep = '01001000'

        brasilapi_response = {
            'cep': '01001000',
            'state': 'SP',
            'city': 'São Paulo',
            'neighborhood': 'Sé',
            'street': 'Praça da Sé',
        }

        with aioresponses() as mocked:
            # ViaCEP fails
            mocked.get(
                f'https://viacep.com.br/ws/{cep}/json/',
                status=500,
            )

            # BrasilAPI succeeds
            mocked.get(
                f'https://brasilapi.com.br/api/cep/v1/{cep}',
                payload=brasilapi_response,
                status=200,
            )

            cep_fetch = CepFetch(providers=[ViaCepProvider(), BrasilApiProvider()])
            result = await cep_fetch.search(cep)

            assert result.service == 'brasilapi'

    async def test_search_with_all_providers_using_default(self):
        """Test search using all default providers."""
        cep = '01001000'

        viacep_response = {
            'cep': '01001-000',
            'uf': 'SP',
            'localidade': 'São Paulo',
            'bairro': 'Sé',
            'logradouro': 'Praça da Sé',
        }

        brasilapi_response = {
            'cep': '01001000',
            'state': 'SP',
            'city': 'São Paulo',
            'neighborhood': 'Sé',
            'street': 'Praça da Sé',
        }

        opencep_response = {
            'cep': '01001-000',
            'uf': 'SP',
            'localidade': 'São Paulo',
            'bairro': 'Sé',
            'logradouro': 'Praça da Sé',
        }

        apicep_response = {
            'code': '01001-000',
            'state': 'SP',
            'city': 'São Paulo',
            'district': 'Sé',
            'address': 'Praça da Sé',
        }

        with aioresponses() as mocked:
            mocked.get(
                f'https://cdn.apicep.com/file/apicep/{cep}.json',
                payload=apicep_response,
                status=200,
            )

            mocked.get(
                f'https://brasilapi.com.br/api/cep/v1/{cep}',
                payload=brasilapi_response,
                status=200,
            )

            mocked.get(
                f'https://opencep.com/v1/{cep}',
                payload=opencep_response,
                status=200,
            )

            mocked.get(
                f'https://viacep.com.br/ws/{cep}/json/',
                payload=viacep_response,
                status=200,
            )

            cep_fetch = CepFetch()  # Uses all default providers
            result = await cep_fetch.search(cep)

            # One of the providers should have responded
            assert result.service in ['viacep', 'brasilapi', 'opencep', 'apicep']
            assert result.state == 'SP'
            assert result.city == 'São Paulo'

    @pytest.mark.parametrize(
        'provider_class,api_url,response_data,expected_service',
        [
            (
                ViaCepProvider,
                'https://viacep.com.br/ws/01001000/json/',
                {
                    'cep': '01001-000',
                    'uf': 'SP',
                    'localidade': 'São Paulo',
                    'bairro': 'Sé',
                    'logradouro': 'Praça da Sé',
                },
                'viacep',
            ),
            (
                BrasilApiProvider,
                'https://brasilapi.com.br/api/cep/v1/01001000',
                {'cep': '01001000', 'state': 'SP', 'city': 'São Paulo', 'neighborhood': 'Sé', 'street': 'Praça da Sé'},
                'brasilapi',
            ),
            (
                OpenCepProvider,
                'https://opencep.com/v1/01001000',
                {
                    'cep': '01001-000',
                    'uf': 'SP',
                    'localidade': 'São Paulo',
                    'bairro': 'Sé',
                    'logradouro': 'Praça da Sé',
                },
                'opencep',
            ),
            (
                ApiCepProvider,
                'https://cdn.apicep.com/file/apicep/01001000.json',
                {'code': '01001-000', 'state': 'SP', 'city': 'São Paulo', 'district': 'Sé', 'address': 'Praça da Sé'},
                'apicep',
            ),
        ],
    )
    async def test_search_with_each_provider_individually(
        self, provider_class, api_url: str, response_data: dict, expected_service: str
    ):
        """Test search with each provider individually."""
        cep = '01001000'

        with aioresponses() as mocked:
            mocked.get(api_url, payload=response_data, status=200)

            provider = provider_class()
            cep_fetch = CepFetch(providers=[provider])
            result = await cep_fetch.search(cep)

            assert result.service == expected_service
            assert result.state == 'SP'
            assert result.city == 'São Paulo'

    async def test_search_multiple_providers_all_fail(self):
        """Test search when all providers fail."""
        cep = '99999999'

        with aioresponses() as mocked:
            # All providers return errors
            mocked.get(
                f'https://viacep.com.br/ws/{cep}/json/',
                payload={'erro': True},
                status=200,
            )

            mocked.get(
                f'https://brasilapi.com.br/api/cep/v1/{cep}',
                status=404,
            )

            mocked.get(
                f'https://opencep.com/v1/{cep}',
                status=404,
            )

            mocked.get(
                f'https://cdn.apicep.com/file/apicep/{cep}.json',
                status=404,
            )

            cep_fetch = CepFetch()
            with pytest.raises(ValueError, match='não encontrado em nenhum provider'):
                await cep_fetch.search(cep)

    async def test_search_two_providers_one_fails_one_succeeds(self):
        """Test search with two providers where one fails and one succeeds."""
        cep = '01001000'

        brasilapi_response = {
            'cep': '01001000',
            'state': 'SP',
            'city': 'São Paulo',
            'neighborhood': 'Sé',
            'street': 'Praça da Sé',
        }

        with aioresponses() as mocked:
            # ViaCEP returns error
            mocked.get(
                f'https://viacep.com.br/ws/{cep}/json/',
                payload={'erro': True},
                status=200,
            )

            # BrasilAPI succeeds
            mocked.get(
                f'https://brasilapi.com.br/api/cep/v1/{cep}',
                payload=brasilapi_response,
                status=200,
            )

            cep_fetch = CepFetch(providers=[ViaCepProvider(), BrasilApiProvider()])
            result = await cep_fetch.search(cep)

            assert result.service == 'brasilapi'
            assert result.cep == '01001000'

    async def test_search_with_formatted_cep(self):
        """Test search with formatted CEP (with dash)."""
        cep = '01001-000'
        clean_cep = '01001000'

        viacep_response = {
            'cep': '01001-000',
            'uf': 'SP',
            'localidade': 'São Paulo',
            'bairro': 'Sé',
            'logradouro': 'Praça da Sé',
        }

        with aioresponses() as mocked:
            mocked.get(
                f'https://viacep.com.br/ws/{clean_cep}/json/',
                payload=viacep_response,
                status=200,
            )

            cep_fetch = CepFetch(providers=[ViaCepProvider()])
            result = await cep_fetch.search(cep)

            assert result.service == 'viacep'
            assert result.cep == '01001-000'
