# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""HTML sanitized string field."""

import bleach

from .sanitizedunicode import SanitizedUnicode

#: Allowed tags used for html sanitizing by bleach.
ALLOWED_HTML_TAGS = [
    'a',
    'abbr',
    'acronym',
    'b',
    'blockquote',
    'br',
    'code',
    'div',
    'em',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'i',
    'li',
    'ol',
    'p',
    'pre',
    'span',
    'strike',
    'strong',
    'sub',
    'sup',
    'u',
    'ul',
]

#: Allowed attributes used for html sanitizing by bleach.
ALLOWED_HTML_ATTRS = {
    '*': ['class'],
    'a': ['href', 'title', 'name', 'class', 'rel'],
    'abbr': ['title'],
    'acronym': ['title'],
}


class SanitizedHTML(SanitizedUnicode):
    """String field which strips sanitizes HTML using the bleach library."""

    def __init__(self, tags=None, attrs=None, *args, **kwargs):
        """Initialize field."""
        super().__init__(*args, **kwargs)
        self.tags = tags or ALLOWED_HTML_TAGS
        self.attrs = attrs or ALLOWED_HTML_ATTRS

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize string by sanitizing HTML."""
        value = super()._deserialize(
            value, attr, data, **kwargs)
        return bleach.clean(
            value,
            tags=self.tags,
            attributes=self.attrs,
            strip=True,
        ).strip()
