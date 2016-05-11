import asyncio
from asyncio import subprocess


class DockerDaemonContext(object):

    def __init__(self, host):
        self._host = host

    async def open(self):
        self._process = await asyncio.create_subprocess_exec(
            "docker",
            "daemon",
            "-H",
            self._host,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        loop = asyncio.get_event_loop()

        # Wait for startup
        while True:
            line = await self._process.stdout.readline()
            if b'API listen on' in line:
                break

        return self

    async def close(self):
        self._process.terminate()
        await self._process.wait()

    async def __aenter__(self):
        return await self.open()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
