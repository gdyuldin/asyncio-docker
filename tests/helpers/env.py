import os.path
from os import environ

print(environ)
def environ_get(key, default=None):
    return environ.get('TEST_%s' % key, default)

DOCKER_DIND_IMAGE = environ_get('DOCKER_DIND_IMAGE', 'docker:1.11.1-dind')
DOCKER_HOST = environ_get('DOCKER_HOST', 'tcp://127.0.0.1:2375')
DOCKER_TLS_HOST = environ_get('DOCKER_TLS_HOST', 'tcp://127.0.0.1:2376')
DOCKER_SOCKET = environ_get('DOCKER_SOCKET', 'unix:///tmp/docker.sock')
SSL_DIR = 'tests/ssl'
SSL_MOUNT_DIR = '/ssl'

TLS_CA_CERT = 'ca.crt'
TLS_SERVER_CERT = 'server.crt'
TLS_SERVER_KEY = 'server.key'
TLS_CLIENT_CERT = 'client.crt'
TLS_CLIENT_KEY = 'client.key'
