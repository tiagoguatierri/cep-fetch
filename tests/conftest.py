"""Pytest configuration and shared fixtures."""

import pytest
from aiohttp import ClientSession

from cep_fetch.core.domain import CepResult


@pytest.fixture
def valid_cep() -> str:
    """Returns a valid CEP for testing."""
    return '01001000'


@pytest.fixture
def invalid_cep() -> str:
    """Returns an invalid CEP for testing."""
    return '99999999'


@pytest.fixture
def cep_result_viacep() -> CepResult:
    """Returns a mock CepResult from ViaCEP."""
    return CepResult(
        cep='01001-000',
        state='SP',
        city='São Paulo',
        neighborhood='Sé',
        street='Praça da Sé',
        service='viacep',
    )


@pytest.fixture
def cep_result_brasilapi() -> CepResult:
    """Returns a mock CepResult from BrasilAPI."""
    return CepResult(
        cep='01001000',
        state='SP',
        city='São Paulo',
        neighborhood='Sé',
        street='Praça da Sé',
        service='brasilapi',
    )


@pytest.fixture
def cep_result_opencep() -> CepResult:
    """Returns a mock CepResult from OpenCEP."""
    return CepResult(
        cep='01001-000',
        state='SP',
        city='São Paulo',
        neighborhood='Sé',
        street='Praça da Sé',
        service='opencep',
    )


@pytest.fixture
def cep_result_apicep() -> CepResult:
    """Returns a mock CepResult from ApiCEP."""
    return CepResult(
        cep='01001-000',
        state='SP',
        city='São Paulo',
        neighborhood='Sé',
        street='Praça da Sé',
        service='apicep',
    )


@pytest.fixture
async def aiohttp_session() -> ClientSession:
    """Returns an aiohttp ClientSession."""
    session = ClientSession()
    yield session
    await session.close()
