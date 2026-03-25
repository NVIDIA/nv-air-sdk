##
## SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
## SPDX-License-Identifier: MIT
##

# `ENV_FILE` is exported in order to preserve its value
# across resulting processes
export ENV_FILE ?= $(CURDIR)/.env
-include ${ENV_FILE}

# General
PROJECT_NAME ?= ${USER}
POETRY ?= poetry
VERSION ?= $(shell ${POETRY} version --short)
PYTHON = ${POETRY} run python

mypy:
	${PYTHON} -m mypy src

ruff:
	${PYTHON} -m ruff format
	${PYTHON} -m ruff check --fix

check-ruff:
	${PYTHON} -m ruff format --check .
	${PYTHON} -m ruff check .

test:
	${PYTHON} -m coverage run -m pytest

test-no-warnings:
	${PYTHON} -m pytest --disable-warnings

ci: ruff mypy test

# Documentation
docs:
	${POETRY} run sphinx-build docs/source docs/_build/html

docs-clean:
	rm -rf docs/_build

docs-serve:
	${PYTHON} -m http.server --directory docs/_build/html 8000

deploy-docs: docs
	bash scripts/deploy-docs.sh

.PHONY: mypy ruff check-ruff test ci test-no-warnings docs docs-clean docs-serve deploy-docs

