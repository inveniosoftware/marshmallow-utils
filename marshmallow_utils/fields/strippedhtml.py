# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""HTML sanitized string field."""

from marshmallow import fields

from ..html import strip_html


class StrippedHTML(fields.String):
    """String field which strips HTML entities.

    The value is stripped using the bleach library. Any already escaped value
    is being unescaped before return.
    """

    def _serialize(self, value, attr, data, **kwargs):
        """Serialize string by stripping HTML entities."""
        value = super()._serialize(value, attr, data, **kwargs)
        return strip_html(value)
