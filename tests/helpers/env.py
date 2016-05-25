import os.path
from os import environ

DOCKER_HOST = environ.get('DOCKER_HOST', 'tcp://127.0.0.1:2377')
DOCKER_TLS_HOST = environ.get('DOCKER_TLS_HOST', 'tcp://127.0.0.1:2376')
DOCKER_SOCKET = environ.get('DOCKER_SOCKET', 'unix:///tmp/docker.sock')
SSL_DIR = 'tests/ssl'
SSL_MOUNT_DIR = '/ssl'

TLS_CA_CERT = 'ca.crt'
TLS_SERVER_CERT = 'server.crt'
TLS_SERVER_KEY = 'server.key'
TLS_CLIENT_CERT = 'client.crt'
TLS_CLIENT_KEY = 'client.key'
