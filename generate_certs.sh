#!/bin/bash
set -e

mkdir "tests/ssl"
cd "tests/ssl"
CN=localhost

openssl genrsa -out ca.key 4096
openssl req -x509 -subj "/C=US/ST=Oregon/L=Portland/CN=$CN" -new -nodes -days 365 -key ca.key -sha256 -out ca.crt

openssl genrsa -out server.key 4096
openssl req -subj "/CN=$CN" -sha256 -new -key server.key -out server.csr

openssl genrsa -out client.key 4096
openssl req -subj '/CN=$CN' -new -key client.key -out client.csr

echo subjectAltName = IP:127.0.0.1 > extfile.cnf
openssl x509 -req -days 365 -sha256 -in server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt -extfile extfile.cnf

echo extendedKeyUsage = clientAuth > extfile.cnf
openssl x509 -req -days 365 -sha256 -in client.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out client.crt -extfile extfile.cnf

rm -v client.csr server.csr extfile.cnf

chmod -v 0400 ca.key server.key client.key
chmod -v 0444 ca.crt server.crt client.crt
