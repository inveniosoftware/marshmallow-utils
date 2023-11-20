# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test the localization of EDTF string."""

import pytest
from marshmallow import Schema, ValidationError

from marshmallow_utils.fields import EDTFDateString, EDTFDateTimeString


class TestSchemaDate(Schema):
    date = EDTFDateString()


class TestSchemaDateTime(Schema):
    datetime = EDTFDateTimeString()


def test_dump_date():
    assert TestSchemaDate().dump({"date": "2020-09/2020-10"}) == {
        "date": "2020-09/2020-10",
    }


def test_dump_datetime():
    assert TestSchemaDateTime().dump({"datetime": "2020-01-01T10:00:00"}) == {
        "datetime": "2020-01-01T10:00:00",
    }


def test_load_date():
    s = TestSchemaDate()
    assert s.load({"date": "2020-09/2020-10"})
    assert s.load({"date": "2020-01-01"})
    # Invalid
    pytest.raises(ValidationError, s.load, {"date": "2020-09-21garbage"})
    # Not chronological
    pytest.raises(ValidationError, s.load, {"date": "2021/2020"})
    # Interval not supported
    pytest.raises(ValidationError, s.load, {"date": "2020-01-01T10:00:00"})


def test_load_datetime():
    s = TestSchemaDateTime()
    assert s.load({"datetime": "2020-01-01T10:00:00"})
    # Invalid interval
    pytest.raises(
        ValidationError, s.load, {"datetime": "2020-01-01T10:00:00/2020-02-01T10:00:00"}
    )
