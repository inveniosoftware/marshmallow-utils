# SPDX-FileCopyrightText: 2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Context."""

from contextvars import ContextVar

context_schema: ContextVar[dict] = ContextVar("context_schema")
