# SPDX-FileCopyrightText: 2020-2025 CERN.
# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-FileCopyrightText: 2025 KTH Royal Institute of Technology.
# SPDX-FileCopyrightText: 2026 TU Wien.
# SPDX-License-Identifier: MIT

r"""Extras and utilities for Marshmallow.

Currently, this library contains a couple of extra fields that helps with
sanitizing data as shown in the following example:

>>> from marshmallow_utils import fields
>>> from marshmallow import Schema
>>> class MySchema(Schema):
...     trim = fields.TrimmedString()
...     html = fields.SanitizedHTML()
...     text = fields.SanitizedUnicode()
...     isodate = fields.ISODateString()
...
>>> data = MySchema().load({
...    'trim': '    whitespace   ',
...    'html': '<script>evil()</script>',
...    'text': 'PDF copy/paste\u200b\u000b\u001b\u0018 ',
...    'isodate': '1999-10-27',
... })
>>> data['trim']
'whitespace'
>>> data['html']
'evil()'
>>> data['text']
'PDF copy/paste'
>>> data['isodate']
'1999-10-27'

Fields:

- :py:class:`~fields.SanitizedUnicode`: Integrates the
  `ftfy <https://pypi.org/project/ftfy/>`_ for fixing broken unicode text.
- :py:class:`~fields.SanitizedHTML`: Integrates the
  `bleach <https://pypi.org/project/bleach/>`_ for HTML sanitization.
- :py:class:`~fields.ISODateString`: Integrates the
  `arrow <https://pypi.org/project/arrow/>`_ for date parsing.
"""

__version__ = "0.15.2"

__all__ = ("__version__",)
