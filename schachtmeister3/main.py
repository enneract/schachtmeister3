import asyncio
import logging
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path

from schachtmeister3.common import DEFAULT_PORT
from schachtmeister3.judge import Judge
from schachtmeister3.udp import UdpServer


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-h', '--host', default='127.0.0.1', help='Hostname or IP to bind the UDP server')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help='UDP port to bind')
    parser.add_argument('-s', '--schachts', required=True, type=Path, help='Path to schachts.list file')
    return parser


def parse_args(argv: Sequence[str] | None = None) -> Namespace:
    return _build_parser().parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG)

    judge = Judge()
    udp_server = UdpServer((args.host, args.port), judge.judge)
    asyncio.run(udp_server.listen())


if __name__ == '__main__':
    main()
