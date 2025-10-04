import logging
import re
from asyncio import (
    BaseTransport,
    DatagramProtocol,
    DatagramTransport,
    Future,
    Task,
    create_task,
    current_task,
    get_running_loop,
)
from ipaddress import IPv4Address
from typing import Any

from schachtmeister3.common import QUAKE_OOB_HEADER, Address, JudgeFunction

logger = logging.getLogger(__name__)


_RE_SM2_QUERY = re.compile(QUAKE_OOB_HEADER + rb'sm2query (\d+\.\d+\.\d+\.\d+)')


class UdpServer:
    def __init__(self, listen_address: Address, judge: JudgeFunction) -> None:
        self.listen_address = listen_address
        self.judge = judge

        self.transport: DatagramTransport | None = None
        self.tasks: set[Task[Any]] = set()

    async def handle_request(self, data: bytes, address: Address) -> None:
        assert self.transport

        if not (match := _RE_SM2_QUERY.match(data)):
            return

        query_address = IPv4Address(match.group(1).decode('ascii'))
        judgement = await self.judge(query_address)
        response = QUAKE_OOB_HEADER + f'sm2reply {query_address} {judgement}'.encode('ascii')
        self.transport.sendto(response, address)

    async def listen(self) -> None:
        parent = self

        # FIXME: I don't like how clusterfucked the code is here
        # _Protocol and UdpServer should have better separation
        class _Protocol(DatagramProtocol):
            def connection_made(self, transport: BaseTransport) -> None:
                assert isinstance(transport, DatagramTransport)
                parent.transport = transport

            def datagram_received(self, data: bytes, address: Address) -> None:
                async def handle_request(data: bytes, address: Address) -> None:
                    try:
                        await parent.handle_request(data, address)
                    finally:
                        if task := current_task():
                            parent.tasks.remove(task)

                task = create_task(handle_request(data, address))
                parent.tasks.add(task)

        transport, protocol = await get_running_loop().create_datagram_endpoint(
            lambda: _Protocol(),
            local_addr=self.listen_address,
        )

        logger.info(f'Listening on {self.listen_address} (UDP)')

        try:
            await Future()
        finally:
            for task in self.tasks:
                logger.warning(f'Exit: cancelling {task}')
                task.cancel()
            transport.close()
