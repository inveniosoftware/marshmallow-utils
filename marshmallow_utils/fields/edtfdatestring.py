# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Extended Date(/Time) Format Level 0 date string field."""

from edtf.parser.grammar import ParseException, level0Expression
from marshmallow import fields


def _(x):
    return x


class EDTFDateString(fields.Str):
    """
    Extended Date(/Time) Format Level 0 date string field.

    Made a field for stronger semantics than just a validator.
    """

    default_error_messages = {
        "invalid": _("Please provide a valid date or interval.")
    }

    def _parse_date_string(self, datestring):
        """Parse input string as EDTF."""
        parser = level0Expression("level0")
        try:
            result = parser.parseString(datestring)
            if not result:
                raise ParseException()

            # check it is chronological if interval
            # NOTE: EDTF Date and Interval both have same interface
            #       and date.lower_strict() <= date.upper_strict() is always
            #       True for a Date
            result = result[0]
            if result.upper_strict() < result.lower_strict():
                raise self.make_error("invalid")
            return result
        except ParseException:
            raise self.make_error("invalid")

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize an EDTF Level 0 formatted date string.

        load()-equivalent operation.

        NOTE: Level 0 allows for an interval.
        NOTE: ``level0Expression`` tries hard to parse dates. For example,
              ``"2020-01-02garbage"`` will parse to the 2020-01-02 date.
        """
        result = self._parse_date_string(value)
        return (
            super(EDTFDateString, self)
            ._deserialize(str(result), attr, data, **kwargs)
        )
