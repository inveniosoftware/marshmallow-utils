# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""HTML sanitized string field."""

import html

import bleach
from marshmallow import fields


class StrippedHTML(fields.String):
    """String field which strips HTML entities.

    The value is stripped using the bleach library. Any already escaped value
    is being unescaped before return.
    """

    def _serialize(self, value, attr, data, **kwargs):
        """Serialize string by stripping HTML entities."""
        value = super()._serialize(
            value, attr, data, **kwargs)
        # Disallow all HTML tags and attributes
        value = bleach.clean(
            value,
            tags=[],
            attributes=[],
            strip=True,
        ).strip()
        # If value has already escaped HTML then return the unescaped value
        return html.unescape(value)
