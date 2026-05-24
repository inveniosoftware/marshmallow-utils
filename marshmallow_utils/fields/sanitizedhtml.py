# SPDX-FileCopyrightText: 2016-2021 CERN.
# SPDX-License-Identifier: MIT

"""HTML sanitized string field."""

from marshmallow import fields

# For backward compatibility we import ALLOWED_* variables.
from ..html import ALLOWED_HTML_ATTRS, ALLOWED_HTML_TAGS, sanitize_html


class SanitizedHTML(fields.String):
    """String field which sanitizes HTML using the bleach library.

    The default list of allowed tags and attributes is defined by
    ``ALLOWED_HTML_TAGS`` and ``ALLOWED_HTML_ATTRS``.

    You can override the defaults like this:

    .. code-block:: python

        class MySchema(Schema):
            html = fields.SanitizedHTML(tags=['a'], attrs={'a': ['href']})

    :param tags: List of allowed tags.
    :param attrs: Dictionary of allowed attributes per tag.
    """

    def __init__(self, tags=None, attrs=None, *args, **kwargs):
        """Initialize field."""
        super().__init__(*args, **kwargs)
        self.tags = tags
        self.attrs = attrs

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize string by sanitizing HTML."""
        value = super()._deserialize(value, attr, data, **kwargs)
        return sanitize_html(value, tags=self.tags, attrs=self.attrs)
