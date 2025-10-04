from ipaddress import IPv4Address


async def whois(address: IPv4Address) -> str:
    raise NotImplementedError('WHOIS lookup not implemented yet')


async def _cached_whois(address: IPv4Address) -> str:
    # TODO
    return await whois(address)


class Judge:
    def __init__(self) -> None:
        pass

    async def judge(self, address: IPv4Address) -> int:
        return 420  # TODO
