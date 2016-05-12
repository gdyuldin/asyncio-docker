import asyncio
import logging
from asyncio import subprocess

from .env import (
    DOCKER_HOST,
    DOCKER_TLS_HOST,
    DOCKER_SOCKET,
    TLS_CA_CERT,
    TLS_SERVER_CERT,
    TLS_SERVER_KEY
)


logger = logging.getLogger('nose2.plugins.daemon')


class DockerDaemon(object):

    def __init__(self, host, tls_verify=False, tls_ca_cert=None,
            tls_cert=None, tls_key=None):

        self._host = host
        self._tls_verify = tls_verify
        self._tls_ca_cert = tls_ca_cert
        self._tls_cert = tls_cert
        self._tls_key = tls_key

    async def open(self):
        command = [
            "docker",
            "daemon",
            "-H",
            self._host,
        ]

        if self._host != DOCKER_SOCKET:
            command.extend([
                "-H",
                DOCKER_SOCKET
            ])

        if self._tls_verify:
            command.extend(['--tlsverify'])

        if self._tls_ca_cert:
            command.extend(['--tlscacert', self._tls_ca_cert])

        if self._tls_cert:
            command.extend(['--tlscert', self._tls_cert])

        if self._tls_key:
            command.extend(['--tlskey', self._tls_key])

        logger.info("Starting [%s]" % ' '.join(command))
        self._process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        loop = asyncio.get_event_loop()

        # Wait for startup, at max 30 seconds
        await asyncio.wait_for(self._wait_startup(), 30)
        return self

    async def _wait_startup(self):
        while True:
            # Read all lines timeout after a second
            try:
                line = await asyncio.wait_for(self._process.stdout.readline(), 3)
            except asyncio.TimeoutError:
                # Wait is over
                return

    async def close(self):
        clean = await asyncio.create_subprocess_exec(
            'docker-clean',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        await clean.wait()

        self._process.terminate()
        await self._process.wait()

    async def __aenter__(self):
        return await self.open()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def tcp_daemon():
    return DockerDaemon(DOCKER_HOST)

def tcp_tls_daemon():
    return DockerDaemon(
        DOCKER_TLS_HOST,
        tls_verify=True,
        tls_ca_cert=TLS_CA_CERT,
        tls_cert=TLS_SERVER_CERT,
        tls_key=TLS_SERVER_KEY,
    )

def unix_daemon():
    return DockerDaemon(DOCKER_SOCKET)
