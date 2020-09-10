# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test the marshmallow fields."""

from datetime import date

import pytest
from marshmallow import Schema, ValidationError

from marshmallow_utils import fields


def test_trimmed():
    """Test trimmed string field."""
    class ASchema(Schema):
        f = fields.TrimmedString()

    assert ASchema().load({'f': '   '}) == {'f': ''}
    assert ASchema().load({'f': '  ad sf '}) == {'f': 'ad sf'}


def test_sanitized_unicode():
    """Test sanitized unicode field."""
    class ASchema(Schema):
        f = fields.SanitizedUnicode()

    assert ASchema().load({'f': ' \u200b\u000b\u001b\u0018 '}) == {'f': ''}


def test_sanitized_html():
    """Test sanitized unicode field."""
    class ASchema(Schema):
        f = fields.SanitizedHTML()

    assert ASchema().load({'f': 'an <script>evil()</script> example'}) == {
        'f': 'an evil() example'}


def test_isodate():
    """Test ISO date formatted string."""
    class ASchema(Schema):
        f = fields.ISODateString()

    assert ASchema().dump({'f': '1999-10-27'}) == {'f': '1999-10-27'}
    assert ASchema().dump({'f': 'invalid'}) == {}

    assert ASchema().load({'f': '1999-10-27'}) == {'f': '1999-10-27'}
    pytest.raises(ValidationError, ASchema().load, {'f': 'invalid'})
