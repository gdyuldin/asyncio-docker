from os import environ

DOCKER_HOST = environ.get('DOCKER_HOST', 'tcp://127.0.0.1:2375')
DOCKER_SOCKET = environ.get('DOCKER_SOCKET', 'unix:///var/run/docker.sock')
