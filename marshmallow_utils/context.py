# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Context."""

from contextvars import ContextVar

context_schema: ContextVar[dict] = ContextVar("context_schema")
