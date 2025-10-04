# Schachtmeister Protocol

Schachtmeister speaks a Quake-style UDP protocol composed of single request and response datagrams.

## Transport

- UDP only; the server binds to `DEFAULT_PORT` (1337) by default.
- Messages are prefixed with the four-byte Quake out-of-band header `0xFF 0xFF 0xFF 0xFF`.
- Each request triggers exactly one response; clients should apply a short timeout and retry if desired.

## Requests

```
<0xFF><0xFF><0xFF><0xFF>sm2query <ipv4>
```

- `<ipv4>` is the dotted-quad address being judged.
- Fields are ASCII-encoded and separated by single spaces.

Example:

```
FFFFFFFFsm2query 203.0.113.5
```

(where `FF` bytes are sent as raw `0xFF` values, not literal characters).

## Responses

```
<0xFF><0xFF><0xFF><0xFF>sm2reply <ipv4> <score>
```

- `<ipv4>` echoes the queried address.
- `<score>` is a signed integer summarising WHOIS/RevDNS matches.
- The response body is ASCII-encoded, space-separated text.

Example reply for a positive score of 17:

```
FFFFFFFFsm2reply 203.0.113.5 17
```

Clients should verify the header, opcode (`sm2reply`), and echoed address before trusting the score. Any malformed packet should be discarded.

## Error Handling

The current implementation returns valid replies for all recognised queries. Missing or invalid requests are dropped silently. Clients must handle lack of response (e.g., by retrying or surfacing a timeout to the caller).
