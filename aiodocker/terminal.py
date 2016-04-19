import sys
import asyncio
import termios
import tty


class TerminalExit(Exception):
    pass

class Terminal(object):

    def __init__(self, stream, stdin=None, stdout=None, stderr=None, loop=None):
        self._stream = stream
        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr
        self._loop = loop or asyncio.get_event_loop()

    async def __aenter__(self):

        # Hookup to stdin
        self._reader = asyncio.StreamReader()
        reader_protocol = asyncio.StreamReaderProtocol(self._reader)

        # Exception ignored https://github.com/python/asyncio/pull/326
        # will fix
        await self._loop.connect_read_pipe(lambda: reader_protocol, self._stdin)

        self._fd = sys.stdin.fileno()
        self._old_settings = termios.tcgetattr(self._fd)
        tty.setraw(self._fd)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)

    async def communicate(self):

        stdios = {
            'stdin': self._stdin,
            'stdout': self._stdout,
            'stderr': self._stderr
        }

        async def read():
            async for data in self._stream:
                stdio = stdios.get(data['type'], None)
                if stdio is not None:
                    stdio.write(data['msg'])
                    stdio.flush()
            raise TerminalExit

        async def write():
            while True:
                data = await self._reader.read(1)
                await self._stream.write(data)

        try:
            await asyncio.gather(read(), write())
        except TerminalExit:
            pass
