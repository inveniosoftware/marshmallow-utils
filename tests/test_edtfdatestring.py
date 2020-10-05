# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test the marshmallow EDTF Date String."""

import pytest
from marshmallow import Schema, ValidationError

from marshmallow_utils.fields import EDTFDateString


class MySchema(Schema):
    edtfdate = EDTFDateString()


@pytest.mark.parametrize('date, expected_date',
                         [("2020-01-02garbage", "2020-01-02"),
                          ("2020-01-45", "2020-01")])
def test_deserialize_assert(date, expected_date):
    assert MySchema().load({'edtfdate': date}) == {'edtfdate': expected_date}


@pytest.mark.parametrize('date', [("2020-08/1998-08"), ("12-040-400")])
def test_deserialize_raise(date):
    pytest.raises(ValidationError, MySchema().load, {'edtfdate': date})
