# Schachtmeister3

Schachtmeister3 is a Python rewrite of [Schachtmeister2](https://redman.xyz/git/schachtmeister2/), a toolkit for spotting VPN use and ban evasion by inspecting WHOIS data and reverse DNS (RevDNS) records. The rewrite is a collaboration between Paweł Redman and gpt-5-codex.[^schacht]

## What It Does
- Listens for UDP queries from game servers (e.g., Unvanquished) and returns a score based on WHOIS and RevDNS matches.
- Parses a `schachts.list` file describing known-good and known-bad signatures.
- Exposes a development client that mimics the Unvanquished integration for quick manual checks.

## Getting Started
1. **Install dependencies**: the project is managed with [uv](https://docs.astral.sh/uv/). Ensure uv and Python 3.10+ are available.
2. **Prepare a `schachts.list` file**: follow the format shown in `schachts.list.example`. Each entry is `whois|revdns <score> "needle"` with optional `//` comments.
3. **Run the daemon**:
   ```bash
   uv run python -m schachtmeister3.main -l 0.0.0.0 -p 1337 -s /path/to/schachts.list
   ```
4. **Query from the development client**:
   ```bash
   uv run python -m schachtmeister3.client --host 127.0.0.1 --port 1337 203.0.113.5
   ```
   The client prints the score returned by the daemon.
5. **Project checks**: lint, type-check, and tests are wrapped in `scripts/check`.
   ```bash
   ./scripts/check
   ```

## `schachts.list` Format
- `whois` entries match substrings in WHOIS output.
- `revdns` entries match hostnames or DNS suffixes.
- Scores are signed integers; multiple matches are summed.
- Lines may contain `//` comments; blank lines are ignored.

## Protocol
Schachtmeister speaks a Quake-style single-request UDP protocol.

### Transport
- UDP only; default port is 1337.
- Every packet begins with the four-byte Quake out-of-band header `0xFF 0xFF 0xFF 0xFF`.
- One request yields at most one response. Clients should set a short timeout and retry if desired.

### Request Message
```
<0xFF><0xFF><0xFF><0xFF>sm2query <ipv4>
```
- `<ipv4>` is the dotted-quad address to score.
- Body is ASCII with single-space separators.

Example (raw bytes: `FF FF FF FF 73 6D 32 71 75 65 72 79 20 32 30 33 2E 30.113.5`):
```
FFFFFFFFsm2query 203.0.113.5
```

### Response Message
```
<0xFF><0xFF><0xFF><0xFF>sm2reply <ipv4> <score>
```
- `<ipv4>` echoes the queried address.
- `<score>` is a signed integer summarizing matches.
- Clients must validate the header, opcode (`sm2reply`), and echoed address.

Example (score 17):
```
FFFFFFFFsm2reply 203.0.113.5 17
```

### Error Handling
Malformed or unknown requests are ignored silently. Clients should treat timeouts as failure and may retry.

## Development
- The code is type-checked with `mypy --strict` and linted/formatted by Ruff (`ruff format` and `ruff check`).
- Tests use `pytest` with `pytest-asyncio` and live under the `tests/` directory.
- GitHub Actions runs `./scripts/check` against Python 3.10–3.13 on every push and pull request.

## License & Credits
- Licensed under the GNU General Public License v3. See `LICENSE` for full terms.
- Original C implementation: Paweł Redman — [Schachtmeister2](https://redman.xyz/git/schachtmeister2/).
- Python rewrite: Paweł Redman & gpt-5-codex.

[^schacht]: “Schachtmeister” is intentionally distinct from the German *Schachmeister* (“chess master”). The name riffs on **Ventilationsschacht**, a callout from mapper yalt’s Tremulous level, which players found amusing. “Schacht” became a tongue-in-cheek slur for nuisance players, so the “master of schachts” is the daemon keeping VPN-abusing troublemakers out.
