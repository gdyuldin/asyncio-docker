import unittest

from nose2.tools.params import params

from helpers import aio
from helpers.daemons import tcp_daemon, tcp_tls_daemon, unix_daemon
from helpers.clients import tcp_client, tcp_tls_client, unix_client

from asyncio_docker.client import ClientError


class ClientTestCase(unittest.TestCase):

    def test_open(self):
        client = tcp_client()
        with client:
            self.assertFalse(client.is_closed())

    def test_closed(self):
        client = tcp_client()
        self.assertTrue(client.is_closed())
        with client:
            pass
        self.assertTrue(client.is_closed())

    def test_closed_request(self):
        client = tcp_client()
        with self.assertRaises(ClientError):
            client.get('/')

    @aio.run_until_complete(30)
    async def test_tcp_connection(self):
        async with tcp_daemon() as daemon:
            with tcp_client() as client:
                async with client.get('/') as res:
                    self.assertEqual(res.status, 404)

    @aio.run_until_complete(30)
    async def test_tcp_tls_connection(self):
        async with tcp_tls_daemon() as daemon:
            with tcp_tls_client() as client:
                async with client.get('/') as res:
                    self.assertEqual(res.status, 404)

    @aio.run_until_complete(30)
    async def test_unix_connection(self):
        async with unix_daemon() as daemon:
            with unix_client() as client:
                async with client.get('/') as res:
                    self.assertEqual(res.status, 404)
