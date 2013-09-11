
test:
	. env/bin/activate; py.test yummly

build:
	./scripts/build_setup.sh

pypi:
	python setup.py sdist upload

.PHONY: test build pypi