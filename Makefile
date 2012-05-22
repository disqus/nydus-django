test:
	pep8 --exclude=migrations --ignore=E501,E225 src/djnydus || exit 1
	pyflakes -x W src/djnydus || exit 1
	coverage run --include=djnydus/* setup.py test && \
	coverage html --omit=*/migrations/* -d cover
