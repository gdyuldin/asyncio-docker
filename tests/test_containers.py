import unittest

from nose2.tools import such
from nose2.tools.params import params

from helpers import aio
from helpers.daemons import tcp_daemon
from helpers.clients import tcp_client


from asyncio_docker.api import API


with such.A('Daemon') as it:

    @it.has_setup
    @aio.run_until_complete()
    async def setup(scenario):
        it.daemon = tcp_daemon()
        it.client = tcp_client()
        it.api = API(it.client)
        it.client.open()
        await it.daemon.open()

    @it.should('list no containers')
    @aio.run_until_complete()
    async def list_no_container(case):
        case.assertEqual(len(await it.api.Container.list()), 0)

    @it.has_teardown
    @aio.run_until_complete()
    async def teardown(scenario):
        it.client.close()
        await it.daemon.close()


it.createTests(globals())
