FQDN ?= localhost
VENV ?= /home/vagrant/venv

release:
	python setup.py sdist
	twine register dist/*
	twine upload dist/*


generate-certs:
	mkdir -p "tests/ssl" && \
		cd "tests/ssl" && \
		openssl genrsa -out ca.key 4096 && \
		openssl req -x509 -subj "/C=US/ST=Oregon/L=Portland/CN=$(FQDN)" -new -nodes -days 365 -key ca.key -sha256 -out ca.crt  && \
		openssl genrsa -out server.key 4096 && \
		openssl req -subj "/CN=$(FQDN)" -sha256 -new -key server.key -out server.csr && \
		openssl genrsa -out client.key 4096 && \
		openssl req -subj "/CN=$(FQDN)" -new -key client.key -out client.csr && \
		echo subjectAltName = IP:127.0.0.1 > extfile.cnf  && \
		openssl x509 -req -days 365 -sha256 -in server.csr -CA ca.crt -CAkey ca.key \
	  	-CAcreateserial -out server.crt -extfile extfile.cnf  && \
		echo extendedKeyUsage = clientAuth > extfile.cnf  && \
		openssl x509 -req -days 365 -sha256 -in client.csr -CA ca.crt -CAkey ca.key \
	  	-CAcreateserial -out client.crt -extfile extfile.cnf  && \
		rm -v client.csr server.csr extfile.cnf


install: generate-certs
	if [ ! -d "$(VENV)" ]; then  \
		virtualenv $(VENV) -p python3.5; \
	fi

	$(VENV)/bin/pip install -r dev_requirements.txt
	$(VENV)/bin/pip install -e .
	sudo docker pull docker:1.11.1-dind


test:
	sudo $(VENV)/bin/green
