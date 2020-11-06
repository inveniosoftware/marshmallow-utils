# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test the localization of EDTF string."""

import pytest
from marshmallow import Schema, ValidationError

from marshmallow_utils.fields import LocalizedEDTFString


class TestSchema(Schema):
    short = LocalizedEDTFString(
        attribute='edtf', format='short', locale='en')
    long = LocalizedEDTFString(
        attribute='edtf', format='long', locale=lambda: 'en')


def test_serializer():
    assert TestSchema().dump({'edtf': '2020-09/2020-10'}) == {
        'short': '9/2020 – 10/2020',
        'long': 'September – October 2020',
    }
