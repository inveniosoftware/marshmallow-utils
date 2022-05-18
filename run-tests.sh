#!/usr/bin/env sh
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 CERN.
# Copyright (C) 2022 Graz University of Technology.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

python -m check_manifest
python -m sphinx.cmd.build -qnN docs docs/_build/html
python -m pytest
tests_exit_code=$?
exit "$tests_exit_code"
