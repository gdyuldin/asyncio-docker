import unittest

from helpers import aio


class ClientTestCase(unittest.TestCase):

    @aio.run_until_complete()
    async def test_connection(self):
        pass
