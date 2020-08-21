#
#
#

.DELETE_ON_ERROR:

PYTHON := python3

VENV := .venv
PIP := $(VENV)/bin/pip
BLACK := $(VENV)/bin/black
PYLINT := $(VENV)/bin/pylint

LINE_LENGTH := 100
PY_FILES := hiscorecounts.py $(shell find ./lib -type f -name '*.py')

## help
help:
.PHONY: help

## venv:
venv: $(VENV)
.PHONY: venv

## lint:
lint: pylint.txt
.PHONY: lint

## format:
format: $(VENV) $(PY_FILES)
	$(BLACK) -l $(LINE_LENGTH) $(PY_FILES)
.PHONY: format

#
#
#

$(VENV): requirements.txt
	$(PYTHON) -m venv $@
	$(PIP) install pip --upgrade
	$(PIP) install setuptools wheel
	$(PIP) install -r requirements.txt
	$(PIP) install pylint black
	touch $@

pylint.txt: $(VENV) $(PY_FILES) .pylintrc
	-$(PYLINT) -f parseable $(PY_FILES) > $@
