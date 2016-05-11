import unittest

from helpers import aio
from helpers.docker import (
    TCP_DAEMON,
    TCP_CLIENT,
    TCP_TLS_DAEMON,
    TCP_TLS_CLIENT,
    UNIX_DAEMON,
    UNIX_CLIENT
)

class ClientTestCase(unittest.TestCase):

    @aio.run_until_complete()
    async def test_tcp_client(self):
        async with TCP_DAEMON as context:
            with TCP_CLIENT as session:
                async with session.get('/') as res:
                    assert res.status == 404

    @aio.run_until_complete()
    async def test_tls_client(self):
        async with TCP_TLS_DAEMON as context:
            with TCP_TLS_CLIENT as session:
                async with session.get('/') as res:
                    assert res.status == 404

    @aio.run_until_complete()
    async def test_unix_client(self):
        async with UNIX_DAEMON as context:
            with UNIX_CLIENT as session:
                async with session.get('/') as res:
                    assert res.status == 404
