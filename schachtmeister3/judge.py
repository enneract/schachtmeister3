import socket
from asyncio import create_subprocess_exec, get_running_loop
from asyncio.subprocess import PIPE
from ipaddress import IPv4Address
from typing import Awaitable, Callable, Generic, TypeVar

_Key = TypeVar('_Key')
_Value = TypeVar('_Value')


class _Cache(Generic[_Key, _Value]):
    def __init__(self, ttl_seconds: float) -> None:
        self._ttl_seconds = ttl_seconds
        self._store: dict[_Key, tuple[float, _Value]] = {}

    async def get(self, key: _Key, loader: Callable[[], Awaitable[_Value]]) -> _Value:
        loop = get_running_loop()
        now = loop.time()
        cached = self._store.get(key)

        if cached:
            expires_at, value = cached
            if now < expires_at:
                return value

        value = await loader()
        self._store[key] = (now + self._ttl_seconds, value)
        return value


async def _whois(address: IPv4Address) -> str:
    process = await create_subprocess_exec(
        'whois',
        str(address),
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode and process.returncode != 0:
        stderr_text = stderr.decode('utf-8', errors='replace').strip()
        detail = f': {stderr_text}' if stderr_text else ''
        raise RuntimeError(f'whois failed for {address}{detail}')

    return stdout.decode('utf-8', errors='replace')


async def _revdns(address: IPv4Address) -> tuple[str, ...]:
    loop = get_running_loop()

    try:
        primary, aliases, _ = await loop.run_in_executor(None, socket.gethostbyaddr, str(address))
    except (socket.herror, socket.gaierror):
        return ()

    seen: set[str] = set()
    results: list[str] = []

    for candidate in (primary, *aliases):
        normalized = candidate.rstrip('.')
        if normalized and normalized not in seen:
            seen.add(normalized)
            results.append(normalized)

    return tuple(results)


class Judge:
    def __init__(self, cache_ttl_seconds: float = 300.0) -> None:
        self._cache_ttl_seconds = cache_ttl_seconds
        self._whois_cache: _Cache[IPv4Address, str] = _Cache(cache_ttl_seconds)
        self._revdns_cache: _Cache[IPv4Address, tuple[str, ...]] = _Cache(cache_ttl_seconds)

    async def _cached_whois(self, address: IPv4Address) -> str:
        async def load() -> str:
            return await _whois(address)

        return await self._whois_cache.get(address, load)

    async def _cached_revdns(self, address: IPv4Address) -> tuple[str, ...]:
        async def load() -> tuple[str, ...]:
            return await _revdns(address)

        return await self._revdns_cache.get(address, load)

    async def judge(self, address: IPv4Address) -> int:
        return 420  # TODO
