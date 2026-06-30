#!/usr/bin/env sh
# SPDX-FileCopyrightText: 2020-2022 CERN.
# SPDX-FileCopyrightText: 2022-2023 Graz University of Technology.
# SPDX-License-Identifier: MIT

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

pybabel extract -F pyproject.toml marshmallow_utils --output-file /dev/null
python -m sphinx.cmd.build -qnN docs docs/_build/html
python -m pytest
tests_exit_code=$?
exit "$tests_exit_code"
