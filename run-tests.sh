#!/usr/bin/env sh
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

check-manifest --ignore ".*-requirements.txt" && \
sphinx-build -qnNW docs docs/_build/html && \
pytest
