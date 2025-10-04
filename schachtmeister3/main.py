import asyncio
import logging

from schachtmeister3.common import DEFAULT_PORT
from schachtmeister3.judge import Judge
from schachtmeister3.udp import UdpServer


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    judge = Judge()
    udp_server = UdpServer(('127.0.0.1', DEFAULT_PORT), judge.judge)
    asyncio.run(udp_server.listen())


if __name__ == '__main__':
    main()
