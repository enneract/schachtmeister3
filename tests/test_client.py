from __future__ import annotations

from ipaddress import IPv4Address
from typing import Any
import socket

import pytest

from schachtmeister3.client import _build_query, _parse_response, request_score


class DummySocket:
    def __init__(self, response: bytes) -> None:
        self._response = response
        self.sent: list[tuple[bytes, tuple[str, int]]] = []
        self.timeout: float | None = None

    def settimeout(self, value: float) -> None:
        self.timeout = value

    def sendto(self, data: bytes, address: tuple[str, int]) -> None:
        self.sent.append((data, address))

    def recvfrom(self, bufsize: int) -> tuple[bytes, Any]:
        return self._response, ('127.0.0.1', 1337)

    def close(self) -> None:  # pragma: no cover - interface requirement
        pass

    def __enter__(self) -> DummySocket:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def make_socket_factory(response: bytes):
    def factory(_family: int, _type: int) -> DummySocket:
        return DummySocket(response)

    return factory


def test_build_query() -> None:
    ip = IPv4Address('203.0.113.5')
    payload = _build_query(ip)
    assert payload.startswith(b'\xff\xff\xff\xffsm2query ')
    assert payload.endswith(b'203.0.113.5')


def test_parse_response_success() -> None:
    ip = IPv4Address('198.51.100.1')
    payload = b'\xff\xff\xff\xffsm2reply 198.51.100.1 42'
    assert _parse_response(ip, payload) == 42


@pytest.mark.parametrize(
    'payload, message',
    [
        (b'bad-header', 'missing quake header'),
        (b'\xff\xff\xff\xffnope', 'unexpected body'),
        (b'\xff\xff\xff\xffsm2reply 203.0.113.5 notanumber', 'Invalid score'),
        (b'\xff\xff\xff\xffsm2reply 203.0.113.6 10', 'Mismatched address'),
    ],
)
def test_parse_response_errors(payload: bytes, message: str) -> None:
    ip = IPv4Address('203.0.113.5')
    with pytest.raises(RuntimeError) as exc:
        _parse_response(ip, payload)
    assert message in str(exc.value)


def test_request_score_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    response = b'\xff\xff\xff\xffsm2reply 203.0.113.5 17'
    factory = make_socket_factory(response)

    result = request_score('example.com', 1234, '203.0.113.5', 1.0, sock_factory=factory)

    assert result == 17


def test_request_score_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    class TimeoutSocket(DummySocket):
        def recvfrom(self, bufsize: int) -> tuple[bytes, Any]:
            raise socket.timeout

    def factory(_family: int, _type: int) -> DummySocket:
        return TimeoutSocket(b'')

    with pytest.raises(TimeoutError):
        request_score('example.com', 1234, '203.0.113.5', 0.1, sock_factory=factory)
