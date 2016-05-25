import asyncio
import unittest

from asyncio import subprocess

import os
import tempfile
from urllib.parse import urlsplit, urlunsplit, urljoin

from .env import (
    DOCKER_HOST,
    DOCKER_TLS_HOST,
    DOCKER_SOCKET,
    DOCKER_DIND_IMAGE,
    SSL_DIR,
    SSL_MOUNT_DIR,
    TLS_CA_CERT,
    TLS_SERVER_CERT,
    TLS_SERVER_KEY
)


class DockerDaemon(object):

    def __init__(self, host, image=DOCKER_DIND_IMAGE, tls_verify=False, tls_ca_cert=None,
            tls_cert=None, tls_key=None):

        self._host = host
        self._image = image
        self._tls_verify = tls_verify
        self._tls_ca_cert = tls_ca_cert
        self._tls_cert = tls_cert
        self._tls_key = tls_key

    @property
    def host(self):
        if self._host.startswith('unix://'):
            o = urlsplit(self._host)
            path = os.path.abspath(os.path.join(self._tmp_dir, os.path.basename(o[2])))
            return 'unix://%s' % path

        return self._host

    async def open(self):
        command = [
            'docker',
            'run',
            '--privileged',
            '--net',
            'host',
            '-v',
            '%s:%s' % (os.path.abspath(SSL_DIR), SSL_MOUNT_DIR),
            '-d'
        ]

        if self._host.startswith('unix://'):
            o = urlsplit(self._host)
            self._tmp_dir = tempfile.mkdtemp()
            command.extend([
                '-v',
                '%s:%s' % (os.path.abspath(self._tmp_dir), os.path.dirname(o[2]))
            ])

        command.extend([
            self._image,
            'docker',
            'daemon',
            '--storage-driver=vfs',
            '-H',
            self._host
        ])

        if self._tls_verify:
            command.extend(['--tlsverify'])

        if self._tls_ca_cert:
            command.extend(['--tlscacert', os.path.join(SSL_MOUNT_DIR, self._tls_ca_cert)])

        if self._tls_cert:
            command.extend(['--tlscert', os.path.join(SSL_MOUNT_DIR, self._tls_cert)])

        if self._tls_key:
            command.extend(['--tlskey', os.path.join(SSL_MOUNT_DIR, self._tls_key)])

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise unittest.SkipTest(stderr)

        self._container = stdout.decode().rstrip()

        try:
            await asyncio.wait_for(self._wait_startup(), 10)
        except asyncio.TimeoutError:
            await self.close()
            raise unittest.SkipTest("Connect timeout")

        return self

    async def _wait_startup(self):
        while True:
            await asyncio.sleep(1)
            returncode, stdout, stderr = await self.call('info')
            if returncode == 0:
                break

    async def _call_host(self, *args):
        command = ['docker']
        command.extend(args)
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        return process.returncode, stdout, stderr

    async def close(self):

        returncode, stdout, stderr = process = await self._call_host(
            'logs',
            self._container
        )

        returncode, stdout, stderr = process = await self._call_host(
            'rm',
            '-f',
            '-v',
            self._container
        )

        if returncode != 0:
            raise Exception(stderr)

        del self._container

    async def call(self, *args):
        command = [
            'docker',
            '-H',
            self.host,
        ]

        if self._tls_verify:
            command.extend(['--tlsverify'])

        if self._tls_ca_cert:
            command.extend(['--tlscacert', os.path.join(SSL_DIR, self._tls_ca_cert)])

        if self._tls_cert:
            command.extend(['--tlscert', os.path.join(SSL_DIR, self._tls_cert)])

        if self._tls_key:
            command.extend(['--tlskey', os.path.join(SSL_DIR, self._tls_key)])

        command.extend(args)

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        return process.returncode, stdout, stderr

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
