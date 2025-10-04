from argparse import ArgumentParser, Namespace
from collections.abc import Sequence

from schachtmeister3.common import DEFAULT_PORT


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-h', '--host', default='127.0.0.1', help='Host on which a Schachtmeister daemon is running')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help='Port number')
    parser.add_argument('address', help='IP address to be judged')
    return parser


def parse_args(argv: Sequence[str] | None = None) -> Namespace:
    return _build_parser().parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    raise NotImplementedError(
        f'Client not yet implemented for {args.address} via {args.host}:{args.port}',
    )


if __name__ == '__main__':
    main()
