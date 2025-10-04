from pathlib import Path

import pytest

from schachtmeister3.schachts import Schachts, SchachtsFileError, load_schachts


def test_load_schachts_from_iterable() -> None:
    entries = [
        '// comment-only line',
        'whois    +10    "Example Corp"',
        'revdns   -5     "bad-host.example" // trailing comment',
    ]

    schachts = load_schachts(entries)

    assert schachts == Schachts(
        whois=[(+10, 'Example Corp')],
        revdns=[(-5, 'bad-host.example')],
    )


def test_load_schachts_from_file(tmp_path: Path) -> None:
    content = '\n'.join([
        '// multi-entry example',
        'whois    +1    "Foo"',
        'whois    +2    "Bar"',
        'revdns   -1    "baz.example"',
        '',
    ])
    path = tmp_path / 'schachts.list'
    path.write_text(content)

    schachts = load_schachts(path)

    assert schachts.whois == [(+1, 'Foo'), (+2, 'Bar')]
    assert schachts.revdns == [(-1, 'baz.example')]


@pytest.mark.parametrize(
    'line, error_message',
    [
        ('foo +1 "Bar"', 'Unknown source'),
        ('whois nope "Bar"', 'Invalid score'),
        ('whois +1 Bar', 'Needle must be a quoted string'),
        ('whois +1', 'Invalid entry'),
    ],
)
def test_parse_line_errors(line: str, error_message: str) -> None:
    with pytest.raises(SchachtsFileError) as exc:
        load_schachts([line])

    assert error_message in str(exc.value)
