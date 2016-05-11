DOCKER_HOST = tcp://172.16.100.10:2375

release:
	python setup.py sdist
	twine register dist/*
	twine upload dist/*

test:
	export DOCKER_HOST=$(DOCKER_HOST); ~/.venvs/python35/bin/nose2;
