from asyncio import create_subprocess_exec
from ipaddress import IPv4Address




async def whois(address: IPv4Address) -> str:
    process = await asyncio.create_subprocess_exec(['whois', str(address)])





async def _cached_whois(address: IPv4Address) -> str:
    # TODO
    return await whois(address)


class Judge:
    def __init__(self) -> None:
        pass

    async def judge(self, address: IPv4Address) -> int:
        return 420  # TODO
