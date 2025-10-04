from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


class SchachtsFileError(RuntimeError):
    pass


@dataclass(slots=True)
class Schachts:
    whois: list[tuple[int, str]] = field(default_factory=list)
    revdns: list[tuple[int, str]] = field(default_factory=list)


def _strip_comment(line: str) -> str:
    escaped = False
    in_string = False

    for index, char in enumerate(line):
        if char == '\\' and in_string:
            escaped = not escaped
            continue
        if char == '"' and not escaped:
            in_string = not in_string
            continue
        escaped = False
        if not in_string and line[index:].startswith('//'):
            return line[:index]
    return line


def _parse_line(line: str) -> tuple[str, int, str] | None:
    clean = _strip_comment(line).strip()
    if not clean:
        return None

    try:
        parts = shlex.split(clean)
    except ValueError as exc:
        raise SchachtsFileError(f'Invalid entry: {line.strip()}') from exc

    if len(parts) != 3:
        raise SchachtsFileError(f'Invalid entry: {line.strip()}')

    source, score_str, needle = parts
    if source not in {'whois', 'revdns'}:
        raise SchachtsFileError(f'Unknown source `{source}` in line: {line.strip()}')

    try:
        score = int(score_str)
    except ValueError as exc:
        raise SchachtsFileError(f'Invalid score `{score_str}` in line: {line.strip()}') from exc

    return source, score, needle


def load_schachts(path: Path | str | Iterable[str]) -> Schachts:
    if isinstance(path, (Path, str)):
        lines_iter: Iterable[str]
        with Path(path).open('r', encoding='utf-8') as handle:
            lines_iter = list(handle)
    else:
        lines_iter = path

    schachts = Schachts()

    for raw_line in lines_iter:
        parsed = _parse_line(raw_line)
        if not parsed:
            continue
        source, score, needle = parsed
        target = schachts.whois if source == 'whois' else schachts.revdns
        target.append((score, needle))

    return schachts
