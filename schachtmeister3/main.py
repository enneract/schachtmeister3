import asyncio
import logging

from schachtmeister.common import DEFAULT_PORT
from schachtmeister.judge import Judge
from schachtmeister.udp import UdpServer


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    judge = Judge()
    udp_server = UdpServer(('127.0.0.1', DEFAULT_PORT), judge.judge)
    asyncio.run(udp_server.listen())


if __name__ == '__main__':
    main()
