.PHONY: test install dev venv clean
.ONESHELL:

VENV=.venv
PY_VER=python3.11
PYTHON=./$(VENV)/bin/$(PY_VER)
PIP_INSTALL=$(PYTHON) -m pip install

test:
	$(PYTHON) -m unittest discover

install: venv
	$(PIP_INSTALL) -U pip setuptools wheel
	$(PIP_INSTALL) git+https://github.com/rafelafrance/common_utils.git@main#egg=common_utils
	$(PIP_INSTALL) .

dev: venv
	source $(VENV)/bin/activate
	$(PIP_INSTALL) -U pip setuptools wheel
	$(PIP_INSTALL) -e ../../misc/common_utils
	$(PIP_INSTALL) -e .[dev]
	pre-commit install

venv:
	test -d $(VENV) || $(PY_VER) -m venv $(VENV)

clean:
	rm -r $(VENV)
	find -iname "*.pyc" -delete
