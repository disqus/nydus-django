develop: update-submodules
	# npm install
	pip install -e . --use-mirrors

install-test-requirements:
	pip install "file://`pwd`#egg=nydus-django[tests]"

update-submodules:
	git submodule init
	git submodule update

test: install-test-requirements lint test-python

testloop: install-test-requirements
	pip install pytest-xdist --use-mirrors
	py.test tests -f

test-python:
	@echo "Running Python tests"
	py.test || exit 1
	@echo ""

lint: lint-python

lint-python:
	@echo "Linting Python files"
	flake8 --ignore=E501,E225,E121,E123,E124,E125,E127,E128 src/djnydus
	@echo ""


coverage: install-test-requirements
	py.test --cov=src/djnydus --cov-report=html
