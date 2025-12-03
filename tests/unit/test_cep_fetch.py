"""Tests for CepFetch main class."""

import asyncio

import pytest
from aiohttp import ClientError, ClientSession

from cep_fetch.cep_fetch import CepFetch
from cep_fetch.core.domain import CepResult
from cep_fetch.core.interfaces import Provider


class MockProvider(Provider):
    """Mock provider for testing."""

    def __init__(self, name: str, result: CepResult | None = None, delay: float = 0, should_raise: bool = False):
        self._name = name
        self._result = result
        self._delay = delay
        self._should_raise = should_raise
        self.call_count = 0
        self.was_cancelled = False

    @property
    def name(self) -> str:
        return self._name

    async def get_cep(self, session: ClientSession, cep: str) -> CepResult:
        """Mock get_cep implementation."""
        self.call_count += 1

        try:
            await asyncio.sleep(self._delay)

            if self._should_raise:
                raise ValueError(f'Provider {self._name} failed')

            if self._result is None:
                raise ValueError(f'CEP not found in {self._name}')

            return self._result

        except asyncio.CancelledError:
            self.was_cancelled = True
            raise


class TestCepFetchInit:
    """Tests for CepFetch initialization."""

    def test_init_with_default_providers(self):
        """Test initialization with default providers."""
        cep_fetch = CepFetch()
        assert len(cep_fetch._providers) == 4

    def test_init_with_custom_providers(self):
        """Test initialization with custom providers."""
        mock_provider = MockProvider(
            name='mock',
            result=CepResult(
                cep='01001000',
                state='SP',
                city='São Paulo',
                neighborhood='Sé',
                street='Praça da Sé',
                service='mock',
            ),
        )

        cep_fetch = CepFetch(providers=[mock_provider])
        assert len(cep_fetch._providers) == 1
        assert cep_fetch._providers[0].name == 'mock'


class TestCepFetchSearch:
    """Tests for CepFetch search method."""

    async def test_search_returns_fastest_provider_result(self):
        """Test that search returns the result from the fastest provider."""
        fast_result = CepResult(
            cep='01001000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='fast_provider',
        )

        slow_result = CepResult(
            cep='01001000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='slow_provider',
        )

        fast_provider = MockProvider(name='fast_provider', result=fast_result, delay=0.01)
        slow_provider = MockProvider(name='slow_provider', result=slow_result, delay=0.5)

        cep_fetch = CepFetch(providers=[fast_provider, slow_provider])
        result = await cep_fetch.search('01001000')

        assert result.service == 'fast_provider'
        assert fast_provider.call_count == 1
        assert slow_provider.call_count == 1
        assert slow_provider.was_cancelled is True

    async def test_search_with_one_provider_failing(self):
        """Test search when one provider fails but another succeeds."""
        success_result = CepResult(
            cep='01001000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='success_provider',
        )

        failing_provider = MockProvider(name='failing_provider', should_raise=True, delay=0.01)
        success_provider = MockProvider(name='success_provider', result=success_result, delay=0.02)

        cep_fetch = CepFetch(providers=[failing_provider, success_provider])
        result = await cep_fetch.search('01001000')

        assert result.service == 'success_provider'
        assert failing_provider.call_count == 1
        assert success_provider.call_count == 1

    async def test_search_with_all_providers_failing(self):
        """Test search when all providers fail."""
        failing_provider1 = MockProvider(name='provider1', should_raise=True, delay=0.01)
        failing_provider2 = MockProvider(name='provider2', should_raise=True, delay=0.02)

        cep_fetch = CepFetch(providers=[failing_provider1, failing_provider2])

        with pytest.raises(ValueError, match='não encontrado em nenhum provider'):
            await cep_fetch.search('99999999')

        assert failing_provider1.call_count == 1
        assert failing_provider2.call_count == 1

    async def test_search_cancels_pending_tasks_on_success(self):
        """Test that pending tasks are cancelled when first provider succeeds."""
        fast_result = CepResult(
            cep='01001000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='fast',
        )

        fast_provider = MockProvider(name='fast', result=fast_result, delay=0.01)
        slow_provider1 = MockProvider(name='slow1', result=fast_result, delay=1.0)
        slow_provider2 = MockProvider(name='slow2', result=fast_result, delay=1.5)

        cep_fetch = CepFetch(providers=[fast_provider, slow_provider1, slow_provider2])
        result = await cep_fetch.search('01001000')

        assert result.service == 'fast'
        assert slow_provider1.was_cancelled is True
        assert slow_provider2.was_cancelled is True

    @pytest.mark.parametrize(
        'cep,expected_clean_cep',
        [
            ('01001-000', '01001000'),
            ('01001000', '01001000'),
            ('01.001-000', '01001000'),
        ],
    )
    async def test_search_with_different_cep_formats(self, cep: str, expected_clean_cep: str):
        """Test search with different CEP formats."""
        result = CepResult(
            cep=expected_clean_cep,
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='mock',
        )

        mock_provider = MockProvider(name='mock', result=result, delay=0.01)
        cep_fetch = CepFetch(providers=[mock_provider])

        search_result = await cep_fetch.search(cep)
        assert search_result.cep == expected_clean_cep

    async def test_search_error_message_contains_all_provider_errors(self):
        """Test that error message contains details from all failing providers."""
        failing_provider1 = MockProvider(name='provider1', should_raise=True)
        failing_provider2 = MockProvider(name='provider2', should_raise=True)

        cep_fetch = CepFetch(providers=[failing_provider1, failing_provider2])

        with pytest.raises(ValueError) as exc_info:
            await cep_fetch.search('99999999')

        error_message = str(exc_info.value)
        assert 'provider1' in error_message
        assert 'provider2' in error_message
        assert 'Provider provider1 failed' in error_message
        assert 'Provider provider2 failed' in error_message

    async def test_search_with_single_provider(self):
        """Test search with only one provider."""
        result = CepResult(
            cep='01001000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='single',
        )

        single_provider = MockProvider(name='single', result=result, delay=0.01)
        cep_fetch = CepFetch(providers=[single_provider])

        search_result = await cep_fetch.search('01001000')
        assert search_result.service == 'single'
        assert single_provider.call_count == 1

    async def test_search_with_multiple_providers_same_speed(self):
        """Test search when multiple providers respond at similar speeds."""
        result1 = CepResult(
            cep='01001000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='provider1',
        )

        result2 = CepResult(
            cep='01001000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='provider2',
        )

        provider1 = MockProvider(name='provider1', result=result1, delay=0.01)
        provider2 = MockProvider(name='provider2', result=result2, delay=0.01)

        cep_fetch = CepFetch(providers=[provider1, provider2])
        result = await cep_fetch.search('01001000')

        # One of them should win
        assert result.service in ['provider1', 'provider2']
        assert provider1.call_count == 1
        assert provider2.call_count == 1

    async def test_search_handles_client_error(self):
        """Test that search handles aiohttp ClientError properly."""

        class ErrorProvider(Provider):
            @property
            def name(self) -> str:
                return 'error_provider'

            async def get_cep(self, session: ClientSession, cep: str) -> CepResult:
                raise ClientError('Network error')

        success_result = CepResult(
            cep='01001000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='success',
        )

        error_provider = ErrorProvider()
        success_provider = MockProvider(name='success', result=success_result, delay=0.02)

        cep_fetch = CepFetch(providers=[error_provider, success_provider])
        result = await cep_fetch.search('01001000')

        assert result.service == 'success'


class TestCepFetchConcurrency:
    """Tests for concurrent execution behavior."""

    async def test_providers_run_concurrently(self):
        """Test that all providers are called concurrently, not sequentially."""
        result = CepResult(
            cep='01001000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='fast',
        )

        # If sequential, this would take 0.1 + 0.1 + 0.01 = 0.21s
        # If concurrent, this should take ~0.1s (time of slowest up to success)
        slow_provider1 = MockProvider(name='slow1', should_raise=True, delay=0.1)
        slow_provider2 = MockProvider(name='slow2', should_raise=True, delay=0.1)
        fast_provider = MockProvider(name='fast', result=result, delay=0.01)

        cep_fetch = CepFetch(providers=[slow_provider1, slow_provider2, fast_provider])

        import time

        start = time.time()
        await cep_fetch.search('01001000')
        elapsed = time.time() - start

        # Should be much less than 0.21s (sequential would be)
        assert elapsed < 0.15, 'Providers should run concurrently'

    async def test_all_providers_are_invoked_immediately(self):
        """Test that all providers start their work immediately."""
        result = CepResult(
            cep='01001000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='provider1',
        )

        provider1 = MockProvider(name='provider1', result=result, delay=0.5)
        provider2 = MockProvider(name='provider2', result=result, delay=0.5)
        provider3 = MockProvider(name='provider3', result=result, delay=0.5)

        cep_fetch = CepFetch(providers=[provider1, provider2, provider3])

        # Give a very short time and then let the fast one win
        result = await cep_fetch.search('01001000')

        # All should have been called (started)
        assert provider1.call_count == 1
        assert provider2.call_count == 1
        assert provider3.call_count == 1
