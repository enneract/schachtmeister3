import asyncio
import logging
import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path

from schachtmeister3.common import DEFAULT_PORT
from schachtmeister3.judge import Judge
from schachtmeister3.schachts import load_schachts
from schachtmeister3.udp import UdpServer


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-l', '--listen', default='127.0.0.1', help='Hostname or IP to bind the UDP server')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help='UDP port to bind')
    parser.add_argument('-s', '--schachts', required=True, type=Path, help='Path to schachts.list file')
    parser.add_argument('--log-file', type=Path, help='Optional path to write structured log output')
    return parser


def parse_args(argv: Sequence[str] | None = None) -> Namespace:
    return _build_parser().parse_args(argv)


class _TaskNameFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        task_name = 'main'
        try:
            task = asyncio.current_task()
        except RuntimeError:
            task = None
        if task is not None:
            task_name = task.get_name() or f'task-{id(task):x}'
        setattr(record, 'task_name', task_name)
        return True


def _configure_logging(log_file: Path | None) -> None:
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    for handler in list(root.handlers):
        root.removeHandler(handler)

    task_filter = _TaskNameFilter()
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(levelname)s [%(task_name)s] %(name)s: %(message)s'))
    stream_handler.addFilter(task_filter)
    root.addHandler(stream_handler)

    if log_file is not None:
        resolved = log_file.expanduser()
        if resolved.parent and not resolved.parent.exists():
            resolved.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(resolved, encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s [%(task_name)s] %(name)s: %(message)s'),
        )
        file_handler.addFilter(task_filter)
        root.addHandler(file_handler)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    _configure_logging(args.log_file)

    schachts = load_schachts(args.schachts)
    judge = Judge(schachts)
    udp_server = UdpServer((args.listen, args.port), judge.judge)
    logging.getLogger(__name__).info('Starting UDP listener on %s:%s', args.listen, args.port)
    asyncio.run(udp_server.listen())


if __name__ == '__main__':
    main()
