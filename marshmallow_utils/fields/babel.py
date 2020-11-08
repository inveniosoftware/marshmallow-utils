# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Localized Extended Date(/Time) Format Level 0 date string field."""

import calendar
from datetime import date, datetime

import arrow
from babel.dates import LC_TIME, format_date, format_datetime, format_time
from babel_edtf import format_edtf
from marshmallow import fields


class BabelFormatField(fields.String):
    """Base classe for babel date and time formatting fields.

    The babel format field is used only for dumping.
    """

    def __init__(self, format='medium', locale=LC_TIME, parse=True, **kwargs):
        """Constructor.

        :param format: The format to use (either ``short``, ``medium``,
                       ``long`` or ``full``).
        :param locale: The current locale or a callable returning the current
                       locale.
        """
        self._format = format
        self._locale = locale
        self._parse = parse
        kwargs.setdefault('dump_only', True)
        super().__init__(**kwargs)

    @property
    def locale(self):
        """Get the locale to use."""
        return self._locale() if callable(self._locale) else self._locale

    def parse(self, value, as_time=False, as_date=False, as_datetime=False):
        """Parse the value if it's a string."""
        if not self._parse or not isinstance(value, str):
            return value

        a = arrow.get(value)
        if as_time:
            return a.datetime
        elif as_date:
            return a.date()
        elif as_datetime:
            return a.datetime
        else:
            return a

    def format_value(self, value):
        """Format a given value using the chosen format function."""
        raise NotImplementedError()

    def _serialize(self, value, attr, data, **kwargs):
        """Serialize the value."""
        return super()._serialize(
            self.format_value(value), attr, data, **kwargs)


class FormatDate(BabelFormatField):
    """Format a date object."""

    def format_value(self, value):
        """Format an EDTF date."""
        return format_date(
            self.parse(value, as_date=True),
            format=self._format,
            locale=self.locale
        )


class FormatDatetime(BabelFormatField):
    """Format a datetime object."""

    def __init__(self, tzinfo=None, **kwargs):
        """Constructor."""
        self._tzinfo = tzinfo
        super().__init__(**kwargs)

    @property
    def tzinfo(self):
        """Get the timzone to use."""
        return self._tzinfo() if callable(self._tzinfo) else self._tzinfo

    def format_value(self, value):
        """Format an EDTF date."""
        return format_datetime(
            self.parse(value, as_datetime=True),
            format=self._format,
            tzinfo=self.tzinfo,
            locale=self.locale
        )


class FormatTime(FormatDatetime):
    """Format a time object."""

    def format_value(self, value):
        """Format an EDTF date."""
        return format_time(
            self.parse(value, as_time=True),
            format=self._format,
            tzinfo=self.tzinfo,
            locale=self.locale
        )


class FormatEDTF(BabelFormatField):
    """Format an EDTF-formatted string."""

    def format_value(self, value):
        """Format an EDTF date."""
        return format_edtf(value, format=self._format, locale=self.locale)
