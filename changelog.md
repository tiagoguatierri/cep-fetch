# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-16

### Added

- Initial implementation of CepFetch library for concurrent CEP lookup
- Support for multiple CEP providers: ViaCEP, BrasilAPI, OpenCEP, and ApiCEP
- Concurrent provider execution with automatic task cancellation on first success
- Fallback mechanism when providers fail
- Comprehensive test suite with 54 unit and integration tests
- Test coverage for all providers with parametrized test cases
- Test coverage for concurrent execution and task cancellation
- Test coverage for domain models and interfaces
- Integration tests for multi-provider scenarios
- Development dependencies: pytest, pytest-asyncio, pytest-cov, aioresponses

[0.1.0]: https://github.com/tiagovit/cep-fetch/releases/tag/v0.1.0
