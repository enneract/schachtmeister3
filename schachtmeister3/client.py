from __future__ import annotations

import socket
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from ipaddress import IPv4Address
from typing import Protocol

from schachtmeister3.common import DEFAULT_PORT, QUAKE_OOB_HEADER


class _SocketFactory(Protocol):
    def __call__(self, family: int, type: int) -> socket.socket:  # pragma: no cover - typing helper
        """Construct a socket."""


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-H', '--host', default='127.0.0.1', help='Host running Schachtmeister')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help='UDP port number')
    parser.add_argument('address', help='IPv4 address to judge')
    parser.add_argument('-t', '--timeout', type=float, default=2.0, help='Seconds to wait for a reply')
    return parser


def parse_args(argv: Sequence[str] | None = None) -> Namespace:
    return _build_parser().parse_args(argv)


def _build_query(address: IPv4Address) -> bytes:
    return QUAKE_OOB_HEADER + f'sm2query {address}'.encode('ascii')


def _parse_response(address: IPv4Address, payload: bytes) -> int:
    if not payload.startswith(QUAKE_OOB_HEADER):
        raise RuntimeError('Malformed response: missing quake header')

    body = payload[len(QUAKE_OOB_HEADER) :].decode('ascii', errors='replace').strip()
    parts = body.split()
    if len(parts) != 3 or parts[0] != 'sm2reply':
        raise RuntimeError('Malformed response: unexpected body')

    reply_address = IPv4Address(parts[1])
    if reply_address != address:
        raise RuntimeError(f'Mismatched address in reply: expected {address}, got {reply_address}')

    try:
        return int(parts[2])
    except ValueError as exc:
        raise RuntimeError(f'Invalid score `{parts[2]}` in reply') from exc


def request_score(
    host: str,
    port: int,
    address: str,
    timeout: float,
    sock_factory: _SocketFactory = socket.socket,
) -> int:
    target = IPv4Address(address)
    query = _build_query(target)

    with sock_factory(socket.AF_INET, socket.SOCK_DGRAM) as udp:
        udp.settimeout(timeout)
        udp.sendto(query, (host, port))
        try:
            payload, _ = udp.recvfrom(4096)
        except socket.timeout as exc:
            raise TimeoutError(f'No response from {host}:{port} within {timeout} seconds') from exc

    return _parse_response(target, payload)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    try:
        score = request_score(args.host, args.port, args.address, args.timeout)
    except Exception as exc:  # pragma: no cover - direct CLI passthrough
        raise SystemExit(str(exc)) from exc

    print(f'Schachtmeister score for {args.address}: {score}')


if __name__ == '__main__':
    main()
