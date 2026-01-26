##
## SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

.PHONY: mypy ruff check-ruff test ci test-no-warnings

