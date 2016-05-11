import asyncio
from asyncio import subprocess

from asyncio_docker.client import factory

from .env import (
    DOCKER_HOST,
    DOCKER_TLS_HOST,
    DOCKER_SOCKET,
    TLS_CA_CERT,
    TLS_SERVER_CERT,
    TLS_SERVER_KEY,
    TLS_CLIENT_CERT,
    TLS_CLIENT_KEY
)


class DockerDaemonContext(object):

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

        if self._tls_verify:
            command.extend(['--tlsverify'])

        if self._tls_ca_cert:
            command.extend(['--tlscacert', self._tls_ca_cert])

        if self._tls_cert:
            command.extend(['--tlscert', self._tls_cert])

        if self._tls_key:
            command.extend(['--tlskey', self._tls_key])

        self._process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        loop = asyncio.get_event_loop()

        # Wait for startup
        print("Running %s" % ' '.join(command))
        await asyncio.wait_for(self._wait_startup(), 30)
        return self

    async def _wait_startup(self):
        while True:
            line = await self._process.stdout.readline()
            print(str(line))
            if b'API listen on' in line:
                break

    async def close(self):
        self._process.terminate()
        await self._process.wait()

    async def __aenter__(self):
        return await self.open()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


TCP_DAEMON = DockerDaemonContext(DOCKER_HOST)
TCP_CLIENT = factory(DOCKER_HOST)(DOCKER_HOST)

TCP_TLS_DAEMON = DockerDaemonContext(
    DOCKER_TLS_HOST,
    tls_verify=True,
    tls_ca_cert=TLS_CA_CERT,
    tls_cert=TLS_SERVER_CERT,
    tls_key=TLS_SERVER_KEY,
)

TCP_TLS_CLIENT = factory(DOCKER_TLS_HOST)(
    DOCKER_TLS_HOST,
    tls=True,
    tls_verify=True,
    tls_ca_cert=TLS_CA_CERT,
    tls_cert=TLS_CLIENT_CERT,
    tls_key=TLS_CLIENT_KEY
)

UNIX_DAEMON = DockerDaemonContext(DOCKER_SOCKET)
UNIX_CLIENT = factory(DOCKER_SOCKET)(DOCKER_SOCKET)
