release:
	python setup.py sdist
	twine register dist/*
	twine upload dist/*
