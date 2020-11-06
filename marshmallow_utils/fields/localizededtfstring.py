# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Localized Extended Date(/Time) Format Level 0 date string field."""

import calendar
from datetime import date, datetime

from babel.dates import LC_TIME
from babel_edtf import format_edtf
from marshmallow import fields


class LocalizedEDTFString(fields.String):
    """Localized Extended Date(/Time) Format Level 0 date string field.

    Useful only for dumping.
    """

    def __init__(self, format='medium', locale=LC_TIME, **kwargs):
        """Constructor.

        :param format: The format to use.
        :param locale: The current locale or a callable returning the current
                       locale.
        """
        self._format = format
        self._locale = locale
        kwargs.setdefault('dump_only', True)
        super(LocalizedEDTFString, self).__init__(**kwargs)

    def _serialize(self, value, attr, data, **kwargs):
        """Serialize a localized EDTF level 0 formatted date string."""
        locale = self._locale() if callable(self._locale) else self._locale
        result = format_edtf(value, format=self._format, locale=locale)
        return super(LocalizedEDTFString, self)._serialize(
            result, attr, data, **kwargs)
