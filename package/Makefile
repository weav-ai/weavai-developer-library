clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.log' -delete

install-dev:
	pip install .[dependencies-dev]
	pre-commit install

install:
	pip install .

all: clean installs