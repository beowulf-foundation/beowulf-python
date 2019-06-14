PROJECT := $(shell basename $(shell pwd))
PYTHON_FILES := beowulf beowulfbase setup.py

.PHONY: clean fmt install

clean:
	rm -rf build/ dist/ *.egg-info .eggs/ .tox/ \
		__pycache__/ .cache/ .coverage htmlcov src

fmt:
	yapf --recursive --in-place --style pep8 $(PYTHON_FILES)
	pycodestyle $(PYTHON_FILES)

install:
	python setup.py install
