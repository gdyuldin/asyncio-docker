import unittest

from nose2.tools import such
from nose2.tools.params import params

from helpers import aio
from helpers.daemon import DAEMONS
from helpers.client import CLIENTS


with such.A("client") as it:
    it.uses(SomeLayer)
    with it.having('an expensive fixture'):

        @it.should("do this")
        def do_this(case):
            print(case)

        """
        @it.has_setup
        @aio.run_until_complete()
        @params(daemon)
        async def setup(daemon):
            await daemon.open()

        @it.should("connect")
        @aio.run_until_complete()
        @params(client)
        async def connect(case, client):
            with client as session:
                async with session.get('/') as res:
                    assert res.status == 404

        @it.has_teardown
        @aio.run_until_complete()
        @params(daemon)
        async def teardown(daemon):
            await daemon.close()
            """

it.createTests(globals())
