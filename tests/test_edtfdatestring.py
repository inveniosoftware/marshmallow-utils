# SPDX-FileCopyrightText: 2020-2026 CERN.
# SPDX-License-Identifier: MIT

"""Test the localization of EDTF string."""

import pytest
from marshmallow import Schema, ValidationError

from marshmallow_utils.fields import (
    EDTFDateString,
    EDTFDateTimeString,
    EDTFLevel2DateString,
)
from marshmallow_utils.fields.edtfdatestring import EDTFLevel0Validator


class TestSchemaDate(Schema):
    date = EDTFDateString()


class TestSchemaDateTime(Schema):
    datetime = EDTFDateTimeString()


class TestSchemaLVL2Date(Schema):
    date = EDTFLevel2DateString()


def test_dump_date():
    assert TestSchemaDate().dump({"date": "2020-09/2020-10"}) == {
        "date": "2020-09/2020-10",
    }


def test_dump_datetime():
    assert TestSchemaDateTime().dump({"datetime": "2020-01-01T10:00:00"}) == {
        "datetime": "2020-01-01T10:00:00",
    }


def test_dump_lvl2_date():
    assert TestSchemaDate().dump({"date": "2020-09-XX/2020-10-XX"}) == {
        "date": "2020-09-XX/2020-10-XX",
    }


def test_load_lvl2date():
    s = TestSchemaLVL2Date()
    assert s.load({"date": "2020?"})
    assert s.load({"date": "2020-01-01"})
    assert s.load({"date": "2004-06-~01/2004-06-~20"})
    assert s.load({"date": "2020-01-XX"})


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

    # Negative dates must raise ValidationError
    pytest.raises(ValidationError, s.load, {"date": "-2020"})
    pytest.raises(ValidationError, s.load, {"date": "-2020-10"})
    pytest.raises(ValidationError, s.load, {"date": "-2020-01-01"})

    # Year 0 must also fail
    pytest.raises(ValidationError, s.load, {"date": "0000"})
    pytest.raises(ValidationError, s.load, {"date": "0000-10"})
    pytest.raises(ValidationError, s.load, {"date": "0000-01-01"})

    # '/' must fail because no starting date of the range
    pytest.raises(ValidationError, s.load, {"date": "/0000"})
    pytest.raises(ValidationError, s.load, {"date": "/0000-12"})
    pytest.raises(ValidationError, s.load, {"date": "/0000-05-06"})


def test_load_datetime():
    s = TestSchemaDateTime()
    assert s.load({"datetime": "2020-01-01T10:00:00"})

    # Invalid interval
    pytest.raises(
        ValidationError,
        s.load,
        {"datetime": "2020-01-01T10:00:00/2020-02-01T10:00:00"},
    )


# Valid date-time timezone offsets


def test_load_datetime_negative_timezone_offset_hours():
    s = TestSchemaDateTime()
    assert s.load({"datetime": "2020-01-01T10:00:00-02"}) == {
        "datetime": "2020-01-01T10:00:00-02",
    }


def test_load_datetime_negative_timezone_offset_hours_minutes():
    s = TestSchemaDateTime()
    assert s.load({"datetime": "2020-01-01T10:00:00-02:30"}) == {
        "datetime": "2020-01-01T10:00:00-02:30",
    }


def test_load_datetime_midnight_utc():
    s = TestSchemaDateTime()
    assert s.load({"datetime": "2020-01-01T00:00:00Z"}) == {
        "datetime": "2020-01-01T00:00:00Z",
    }


def test_load_datetime_end_of_day():
    s = TestSchemaDateTime()
    assert s.load({"datetime": "2020-01-01T23:59:59"}) == {
        "datetime": "2020-01-01T23:59:59",
    }


# Invalid date-time values


def test_load_datetime_invalid_hour():
    s = TestSchemaDateTime()
    pytest.raises(ValidationError, s.load, {"datetime": "2020-01-01T25:00:00"})


def test_load_datetime_invalid_minute():
    s = TestSchemaDateTime()
    pytest.raises(ValidationError, s.load, {"datetime": "2020-01-01T10:60:00"})


def test_load_datetime_invalid_second():
    s = TestSchemaDateTime()
    pytest.raises(ValidationError, s.load, {"datetime": "2020-01-01T10:00:60"})


def test_load_datetime_missing_seconds():
    s = TestSchemaDateTime()
    pytest.raises(ValidationError, s.load, {"datetime": "2020-01-01T10:00"})


def test_load_datetime_lvl0_timezones():
    s = TestSchemaDateTime()

    # UTC date-time
    assert s.load({"datetime": "2020-01-01T10:00:00Z"}) == {
        "datetime": "2020-01-01T10:00:00Z",
    }

    # Time zone offset in hours
    assert s.load({"datetime": "2020-01-01T10:00:00+02"}) == {
        "datetime": "2020-01-01T10:00:00+02",
    }

    # Time zone offset in hours and minutes
    assert s.load({"datetime": "2020-01-01T10:00:00+02:00"}) == {
        "datetime": "2020-01-01T10:00:00+02:00",
    }


def test_load_date_lvl0_precision():
    s = TestSchemaDate()

    # Year precision
    assert s.load({"date": "2020"}) == {"date": "2020"}

    # Month precision
    assert s.load({"date": "2020-09"}) == {"date": "2020-09"}

    # Full date precision
    assert s.load({"date": "2020-01-01"}) == {"date": "2020-01-01"}


def test_load_date_intervals():
    s = TestSchemaDate()

    # Year-to-year interval
    assert s.load({"date": "2020/2021"}) == {"date": "2020/2021"}

    # Date-to-date interval
    assert s.load({"date": "2020-01-01/2020-01-05"}) == {
        "date": "2020-01-01/2020-01-05",
    }

    # Mixed precision interval
    assert s.load({"date": "2020-01/2020-02-05"}) == {
        "date": "2020-01/2020-02-05",
    }


def test_load_date_rejects_open_intervals():
    s = TestSchemaDate()
    for value in ("../2020", "2020/..", "/2020", "2020/"):
        pytest.raises(ValidationError, s.load, {"date": value})


def test_load_date_year_boundaries():
    s = TestSchemaDate()
    assert s.load({"date": "9999"}) == {"date": "9999"}
    assert s.load({"date": "0001/9999"}) == {"date": "0001/9999"}


def test_load_date_rejects_unrenderable_years_in_intervals():
    s = TestSchemaDate()
    for value in ("2020/-2026", "2020/0000"):
        pytest.raises(ValidationError, s.load, {"date": value})


def test_load_valid_month_end_dates():
    s = TestSchemaDate()
    assert s.load({"date": "2020-04-30"}) == {"date": "2020-04-30"}
    assert s.load({"date": "2020-12-31"}) == {"date": "2020-12-31"}


def test_load_earliest_positive_year():
    s = TestSchemaDate()
    assert s.load({"date": "0001-01-01"}) == {"date": "0001-01-01"}


# Invalid calendar dates


def test_load_invalid_leap_year_date():
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2021-02-29"})


def test_load_invalid_day_of_month():
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2020-02-30"})


def test_load_invalid_april_date():
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2020-04-31"})


def test_load_invalid_month_13():
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2020-13"})


def test_load_invalid_month_00():
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2020-00"})


def test_load_invalid_day_00():
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2020-01-00"})


# Valid date intervals


def test_load_month_to_month_interval():
    s = TestSchemaDate()
    assert s.load({"date": "2020-01/2020-12"}) == {
        "date": "2020-01/2020-12",
    }


def test_load_year_to_month_interval():
    s = TestSchemaDate()
    assert s.load({"date": "2020/2020-12"}) == {
        "date": "2020/2020-12",
    }


def test_load_month_to_year_interval():
    s = TestSchemaDate()
    assert s.load({"date": "2020-01/2021"}) == {
        "date": "2020-01/2021",
    }


def test_load_day_to_month_interval():
    s = TestSchemaDate()
    assert s.load({"date": "2020-01-01/2020-01"}) == {
        "date": "2020-01-01/2020-01",
    }


def test_load_month_to_day_interval():
    s = TestSchemaDate()
    assert s.load({"date": "2020-01/2020-01-31"}) == {
        "date": "2020-01/2020-01-31",
    }


# Invalid date intervals


def test_load_interval_missing_end_date():
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2020/"})


def test_load_interval_invalid_start_month():
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2020-13/2021"})


def test_load_interval_too_many_endpoints():
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2020/2021/2022"})


def test_load_interval_invalid_end_date():
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2020-01-01/garbage"})


def test_load_season_is_rejected():
    # python-edtf's Season.precision reads _month, which a season never sets
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "2001-21"})


def test_load_partial_unspecified_is_rejected():
    # python-edtf's PartialUnspecified.__init__ calls .startswith on a dict
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "1984-1X"})


def test_load_oversized_years():
    s = TestSchemaDate()
    for value in ("99999", "Y170000002", "Y-170000002", "-9999-12-31"):
        pytest.raises(ValidationError, s.load, {"date": value})


def test_load_year_boundaries():
    s = TestSchemaDate()
    assert s.load({"date": "9999-12-31"}) == {"date": "9999-12-31"}
    assert s.load({"date": "0001-01-01/9999-12-31"}) == {
        "date": "0001-01-01/9999-12-31",
    }


def test_load_open_interval_rejected_by_type():
    # Level1Interval is not an exact Level 0 type, so the type check rejects it
    # before the open bound is compared
    s = TestSchemaDate()
    pytest.raises(ValidationError, s.load, {"date": "1985/.."})


@pytest.mark.xfail(
    raises=AttributeError,
    strict=True,
    reason="without a type filter, an open bound reaches the tm_year check",
)
def test_level0_validator_open_interval_without_types():
    pytest.raises(ValidationError, EDTFLevel0Validator(types=[]), "1985/..")
