import asyncio
from typing import List, Set

import aiohttp

from cep_fetch.core.interfaces import CepResult, Provider
from cep_fetch.providers import ApiCepProvider, BrasilApiProvider, OpenCepProvider, ViaCepProvider


class CepFetch:
    """CepFetch class."""

    def __init__(self, providers: List[Provider] | None = None):
        self._providers = providers or [
            ApiCepProvider(),
            BrasilApiProvider(),
            OpenCepProvider(),
            ViaCepProvider(),
        ]

    async def search(self, cep: str) -> CepResult:
        """Search the CEP in all providers concurrently."""
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks: Set[asyncio.Task[CepResult]] = set()

            for provider in self._providers:
                task = asyncio.create_task(provider.get_cep(session, cep), name=provider.name)
                tasks.add(task)

            errors: List[str] = []

            try:
                while tasks:
                    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                    # Update the tasks list to keep only the pending tasks
                    tasks = pending

                    for task in done:
                        try:
                            result = await task
                            return result

                        except Exception as e:
                            provider_name = task.get_name()
                            errors.append(f'{provider_name}: {str(e)}')

            finally:
                for task in tasks:
                    if not task.done():
                        task.cancel()

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

            error_msg = ' | '.join(errors)
            raise ValueError(f'CEP {cep} não encontrado em nenhum provider. Detalhes: {error_msg}')
