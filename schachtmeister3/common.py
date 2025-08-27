from ipaddress import IPv4Address
from typing import Awaitable, Callable

DEFAULT_PORT = 1337

Address = tuple[str, int]  # Host name / IP address + port

JudgeFunction = Callable[[IPv4Address], Awaitable[int]]

