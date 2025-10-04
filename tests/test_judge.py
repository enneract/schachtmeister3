from ipaddress import IPv4Address

import pytest

from schachtmeister3.judge import Judge
from schachtmeister3.schachts import Schachts


pytestmark = pytest.mark.anyio('asyncio')


async def test_judge_scores_whois_and_revdns(monkeypatch: pytest.MonkeyPatch) -> None:
    schachts = Schachts(
        whois=[(+10, 'Example Corp')],
        revdns=[(-5, 'bad-host.example')],
    )
    judge = Judge(schachts)
    address = IPv4Address('203.0.113.10')

    async def fake_whois(_: IPv4Address) -> str:
        return 'Network: Example Corp\nAbuse: noc@example.com'

    async def fake_revdns(_: IPv4Address) -> tuple[str, ...]:
        return ('bad-host.example',)

    monkeypatch.setattr('schachtmeister3.judge._whois', fake_whois)
    monkeypatch.setattr('schachtmeister3.judge._revdns', fake_revdns)

    result = await judge.judge(address)

    assert result == 5


async def test_judge_revdns_suffix_matching(monkeypatch: pytest.MonkeyPatch) -> None:
    schachts = Schachts(
        whois=[],
        revdns=[(+7, 'trusted.example')],
    )
    judge = Judge(schachts)
    address = IPv4Address('198.51.100.20')

    async def fake_whois(_: IPv4Address) -> str:
        return ''

    async def fake_revdns(_: IPv4Address) -> tuple[str, ...]:
        return ('vpn01.trusted.example',)

    monkeypatch.setattr('schachtmeister3.judge._whois', fake_whois)
    monkeypatch.setattr('schachtmeister3.judge._revdns', fake_revdns)

    result = await judge.judge(address)

    assert result == 7


async def test_judge_no_matches(monkeypatch: pytest.MonkeyPatch) -> None:
    schachts = Schachts(
        whois=[(+10, 'Example Corp')],
        revdns=[(-5, 'bad-host.example')],
    )
    judge = Judge(schachts)
    address = IPv4Address('192.0.2.5')

    async def fake_whois(_: IPv4Address) -> str:
        return 'Other provider'

    async def fake_revdns(_: IPv4Address) -> tuple[str, ...]:
        return ('other.example',)

    monkeypatch.setattr('schachtmeister3.judge._whois', fake_whois)
    monkeypatch.setattr('schachtmeister3.judge._revdns', fake_revdns)

    result = await judge.judge(address)

    assert result == 0
