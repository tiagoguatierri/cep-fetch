# cep-fetch

A Python library for fetching Brazilian postal codes (CEP) from multiple providers concurrently, automatically returning the fastest response.

## Features

- **Concurrent execution**: Queries all providers simultaneously and returns the fastest response
- **Automatic fallback**: If one provider fails, others continue running
- **Task cancellation**: Automatically cancels pending requests when first provider responds
- **Multiple providers**: Supports ViaCEP, BrasilAPI, OpenCEP, and ApiCEP
- **Type safe**: Full type hints support
- **Easy to extend**: Simple interface for adding custom providers
- **Well tested**: Comprehensive test suite with 90%+ coverage

## Installation

```bash
pip install cep-fetch
```

Or using uv:

```bash
uv add cep-fetch
```

## Quick Start

```python
import asyncio
from cep_fetch import CepFetch

async def main():
    cep_fetch = CepFetch()
    result = await cep_fetch.search('01001000')
    
    print(f"CEP: {result.cep}")
    print(f"State: {result.state}")
    print(f"City: {result.city}")
    print(f"Neighborhood: {result.neighborhood}")
    print(f"Street: {result.street}")
    print(f"Provider: {result.service}")

asyncio.run(main())
```

Output:
```
CEP: 01001-000
State: SP
City: São Paulo
Neighborhood: Sé
Street: Praça da Sé
Provider: viacep
```

## Usage Examples

### Basic Usage

```python
from cep_fetch import CepFetch

async def fetch_address():
    cep_fetch = CepFetch()
    result = await cep_fetch.search('01001000')
    return result
```

### Using Specific Providers

You can specify which providers to use:

```python
from cep_fetch import CepFetch
from cep_fetch.providers import ViaCepProvider, BrasilApiProvider

async def fetch_with_specific_providers():
    # Only use ViaCEP and BrasilAPI
    cep_fetch = CepFetch(providers=[
        ViaCepProvider(),
        BrasilApiProvider()
    ])
    
    result = await cep_fetch.search('01001000')
    return result
```

### Error Handling

```python
from cep_fetch import CepFetch

async def fetch_with_error_handling():
    cep_fetch = CepFetch()
    
    try:
        result = await cep_fetch.search('99999999')
        print(f"Found: {result.city}")
    except ValueError as e:
        print(f"Error: {e}")
        # Error: CEP 99999999 não encontrado em nenhum provider. Detalhes: ...
```

### Different CEP Formats

The library automatically handles different CEP formats:

```python
from cep_fetch import CepFetch

async def fetch_different_formats():
    cep_fetch = CepFetch()
    
    # All these formats work
    result1 = await cep_fetch.search('01001000')     # Without dash
    result2 = await cep_fetch.search('01001-000')    # With dash
    result3 = await cep_fetch.search('01.001-000')   # With dots and dash
```

## Available Providers

The library includes four providers out of the box:

| Provider | URL | Format |
|----------|-----|--------|
| ViaCEP | https://viacep.com.br | Free, no rate limit |
| BrasilAPI | https://brasilapi.com.br | Free, no rate limit |
| OpenCEP | https://opencep.com | Free, no rate limit |
| ApiCEP | https://apicep.com | Free, no rate limit |

## Creating a Custom Provider

You can easily create custom providers by implementing the `Provider` interface:

```python
from aiohttp import ClientSession
from cep_fetch import Provider, CepResult

class MyCustomProvider(Provider):
    """Custom CEP provider."""
    
    @property
    def name(self) -> str:
        """Return provider identifier."""
        return 'my_custom_provider'
    
    async def get_cep(self, session: ClientSession, cep: str) -> CepResult:
        """
        Fetch CEP from custom API.
        
        Args:
            session: aiohttp ClientSession for making requests
            cep: The CEP to search (may contain formatting)
        
        Returns:
            CepResult with normalized data
            
        Raises:
            Exception if CEP not found or request fails
        """
        # Clean CEP (remove formatting)
        clean_cep = self._clean_cep(cep)
        
        # Make request to your API
        url = f'https://api.example.com/cep/{clean_cep}'
        
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            
            # Map response to CepResult
            return CepResult(
                cep=data['zipcode'],
                state=data['state'],
                city=data['city'],
                neighborhood=data.get('district'),
                street=data.get('street'),
                service=self.name
            )
```

### Using Your Custom Provider

```python
from cep_fetch import CepFetch
from cep_fetch.providers import ViaCepProvider, BrasilApiProvider

async def use_custom_provider():
    # Use only your custom provider
    cep_fetch = CepFetch(providers=[MyCustomProvider()])
    result = await cep_fetch.search('01001000')
    
    # Or combine with existing providers
    cep_fetch = CepFetch(providers=[
        MyCustomProvider(),
        ViaCepProvider(),
        BrasilApiProvider()
    ])
    result = await cep_fetch.search('01001000')
```

## How It Works

1. **Concurrent Execution**: All providers are queried simultaneously using asyncio tasks
2. **First Response Wins**: The first provider to successfully respond returns the result
3. **Automatic Cancellation**: All pending requests are automatically cancelled once a response is received
4. **Error Aggregation**: If all providers fail, a detailed error message with all failures is returned

```
Provider 1 -----> [Response in 150ms] -----> Cancelled
Provider 2 -----> [Response in 80ms]  -----> RETURNED (fastest)
Provider 3 -----> [Response in 200ms] -----> Cancelled
Provider 4 -----> [Error]             -----> Logged
```

## API Reference

### CepFetch

Main class for fetching CEP data.

#### Constructor

```python
CepFetch(providers: List[Provider] | None = None)
```

**Parameters:**
- `providers` (optional): List of Provider instances to use. If not provided, uses all default providers.

#### Methods

##### search

```python
async def search(cep: str) -> CepResult
```

Search for CEP information across all providers concurrently.

**Parameters:**
- `cep`: Brazilian postal code (with or without formatting)

**Returns:**
- `CepResult`: Result from the fastest responding provider

**Raises:**
- `ValueError`: If all providers fail to find the CEP

### CepResult

Dataclass containing CEP information.

**Attributes:**
- `cep` (str): The postal code
- `state` (str): State abbreviation (e.g., 'SP')
- `city` (str): City name
- `neighborhood` (str | None): Neighborhood name
- `street` (str | None): Street name
- `service` (str): Provider that returned the result

### Provider

Abstract base class for implementing custom providers.

**Methods to implement:**
- `name` (property): Returns provider identifier string
- `get_cep(session, cep)`: Async method that fetches and returns CepResult

**Helper methods:**
- `_clean_cep(cep)`: Removes formatting from CEP string

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/tiagovit/cep-fetch.git
cd cep-fetch

# Install dependencies
uv sync --all-groups

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_cep_fetch.py

# Run specific test
pytest tests/unit/test_cep_fetch.py::TestCepFetchSearch::test_search_returns_fastest_provider_result
```

### Code Quality

```bash
# Format code
ruff format src/

# Lint code
ruff check src/

# Fix linting issues
ruff check --fix src/
```

## Requirements

- Python >= 3.11
- aiohttp >= 3.13.2

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project was inspired by [cep-promise](https://github.com/BrasilAPI/cep-promise), a similar library for Node.js.

## Changelog

See [CHANGELOG.md](changelog.md) for a detailed history of changes.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/tiagovit/cep-fetch/issues) on GitHub.
