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

    def __init__(self, tags=ALLOWED_HTML_TAGS, attrs=ALLOWED_HTML_ATTRS, *args,
                 **kwargs):
        """Initialize field."""
        super().__init__(*args, **kwargs)
        self.tags = tags
        self.attrs = attrs

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
