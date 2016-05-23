import os.path
from os import environ

DOCKER_HOST = environ.get('DOCKER_HOST', 'tcp://127.0.0.1:2377')
DOCKER_TLS_HOST = environ.get('DOCKER_TLS_HOST', 'tcp://127.0.0.1:2376')
DOCKER_SOCKET = environ.get('DOCKER_SOCKET', 'unix:///var/run/docker.sock')
SSL_DIR = 'tests/ssl'

TLS_CA_CERT = os.path.join(SSL_DIR, 'ca.crt')
TLS_SERVER_CERT = os.path.join(SSL_DIR, 'server.crt')
TLS_SERVER_KEY = os.path.join(SSL_DIR, 'server.key')
TLS_CLIENT_CERT = os.path.join(SSL_DIR, 'client.crt')
TLS_CLIENT_KEY = os.path.join(SSL_DIR, 'client.key')
