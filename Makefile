FQDN=localhost

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
		rm -v client.csr server.csr extfile.cnf  && \
		chmod -v 0400 ca.key server.key client.key  && \
		chmod -v 0444 ca.crt server.crt client.crt


dev-install: generate-certs
	curl -s https://raw.githubusercontent.com/ZZROTDesign/docker-clean/v2.0.3/docker-clean | \
	sudo tee /usr/local/bin/docker-clean > /dev/null && \
	sudo chmod +x /usr/local/bin/docker-clean
	virtualenv .venv -p python3.5
	.venv/bin/pip install -r dev_requirements.txt
	.venv/bin/pip install -e .

test:
	sudo .venv/bin/nose2
