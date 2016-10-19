asyncio-docker
==============

Asynchronous docker client for python.

.. image:: https://travis-ci.org/gdyuldin/asyncio-docker2.svg?branch=master
    :target: https://travis-ci.org/gdyuldin/asyncio-docker2

.. image:: https://codecov.io/gh/gdyuldin/asyncio-docker2/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/gdyuldin/asyncio-docker2


Usage
=====

.. code-block:: python

    import asyncio
    from asyncio_docker.client import client_factory
    from asyncio_docker.api import RemoteAPI


    async def list_images(api):
        containers = await api.Image.list()
        return containers


    async def main(loop, docker_url):
        client_class = client_factory(docker_url)
        client = client_class(docker_url, loop=loop)
        client.open()
        api = RemoteAPI(client)
        print(await list_images(api))
        client.close()


    docker_url = 'unix://var/run/docker.sock'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop, docker_url))

Testing
=======

.. code-block:: bash

    export VENV=./.venv
    make install
    make test
