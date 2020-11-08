# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test the babel date and time localization."""

from datetime import date, datetime

import pytest
from babel.dates import get_timezone
from marshmallow import Schema, ValidationError

from marshmallow_utils.fields import FormatDate, FormatDatetime, FormatEDTF, \
    FormatTime


@pytest.fixture()
def dt():
    """Datetime fixture."""
    return datetime(2020, 11, 8, 23, 22)


class MySchema(Schema):
    """Test schema."""

    short = FormatEDTF(attribute='edtf', format='short', locale='en')
    long = FormatEDTF(attribute='edtf', format='long', locale=lambda: 'en')
    datetime = FormatDatetime(format='medium', locale='da')
    time = FormatTime(format='long', locale='da',
                      tzinfo=lambda: get_timezone('America/Chicago'))
    date = FormatDate(format='short', locale='da')
    no_parse = FormatDatetime(format='medium', locale='da', parse=False)


def test_format_edtf():
    """Test EDTF formatting."""
    assert MySchema().dump({'edtf': '2020-09/2020-10'}) == {
        'short': '9/2020 – 10/2020',
        'long': 'September – October 2020',
    }


def test_format_datetime(dt):
    """Test datetime formatting."""
    assert MySchema().dump({'datetime': dt}) == {
        'datetime': '8. nov. 2020 23.22.00',
    }
    assert MySchema().dump({'datetime': dt.isoformat()}) == {
        'datetime': '8. nov. 2020 23.22.00',
    }
    # Test field with no parsing of strings:
    pytest.raises(Exception, MySchema().dump, {'no_parse': dt.isoformat()})


def test_format_time(dt):
    """Test datetime formatting."""
    assert MySchema().dump({'time': dt}) == {'time': '17.22.00 -0600'}
    assert MySchema().dump({
        'time': dt.isoformat()}) == {'time': '17.22.00 -0600'}


def test_format_date(dt):
    """Test datetime formatting."""
    assert MySchema().dump({'date': dt}) == {'date': '08.11.2020'}
    assert MySchema().dump({'date': '2021-01-01'}) == {'date': '01.01.2021'}
