"""Tests for domain models."""

import pytest

from cep_fetch.core.domain import CepResult


class TestCepResult:
    """Tests for CepResult dataclass."""

    def test_create_cep_result_with_all_fields(self):
        """Test creating CepResult with all fields."""
        result = CepResult(
            cep='01001-000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='viacep',
        )

        assert result.cep == '01001-000'
        assert result.state == 'SP'
        assert result.city == 'São Paulo'
        assert result.neighborhood == 'Sé'
        assert result.street == 'Praça da Sé'
        assert result.service == 'viacep'

    def test_create_cep_result_with_optional_fields_none(self):
        """Test creating CepResult with optional fields as None."""
        result = CepResult(
            cep='01001-000',
            state='SP',
            city='São Paulo',
            neighborhood=None,
            street=None,
            service='viacep',
        )

        assert result.cep == '01001-000'
        assert result.state == 'SP'
        assert result.city == 'São Paulo'
        assert result.neighborhood is None
        assert result.street is None
        assert result.service == 'viacep'

    def test_cep_result_is_frozen(self):
        """Test that CepResult is immutable (frozen dataclass)."""
        result = CepResult(
            cep='01001-000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='viacep',
        )

        with pytest.raises(AttributeError):
            result.cep = '02002-000'

    def test_cep_result_equality(self):
        """Test that two CepResult instances with same data are equal."""
        result1 = CepResult(
            cep='01001-000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='viacep',
        )

        result2 = CepResult(
            cep='01001-000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='viacep',
        )

        assert result1 == result2

    def test_cep_result_inequality_different_service(self):
        """Test that CepResult instances with different services are not equal."""
        result1 = CepResult(
            cep='01001-000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='viacep',
        )

        result2 = CepResult(
            cep='01001-000',
            state='SP',
            city='São Paulo',
            neighborhood='Sé',
            street='Praça da Sé',
            service='brasilapi',
        )

        assert result1 != result2
