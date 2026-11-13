# SPDX-FileCopyrightText: 2016-2026 CERN.
# SPDX-License-Identifier: MIT

"""Extended Date(/Time) Format Level 0 date string field."""

import datetime as dt

from babel_edtf import parse_edtf
from edtf import (
    Date,
    DateAndTime,
    Interval,
    Level1Interval,
    Level2Interval,
    OneOfASet,
    UncertainOrApproximate,
)
from marshmallow import ValidationError, fields
from marshmallow.validate import Validator
from pyparsing import ParseException


class EDTFValidator(Validator):
    """EDTF validator."""

    default_message = "Please provide a valid date or interval."

    def __init__(
        self,
        types=[Date, DateAndTime, Interval],
        chronological_interval=True,
        error=None,
    ):
        """Constructor.

        :params types: List of EDTFObject subclasses that you accept. Use
            EDTFObject to accept all levels.
        """
        self._types = types or []
        self._chronological_interval = chronological_interval
        self._error = error or self.default_message

    def _format_error(self, value, e):
        return self._error.format(input=value, edtf=e)

    def __call__(self, value):
        """Validate."""
        try:
            e = parse_edtf(value)
        except ParseException:
            raise ValidationError(self._format_error(value, None))

        if self._types:
            if not any([isinstance(e, t) for t in self._types]):
                raise ValidationError(self._format_error(value, e))

        if self._chronological_interval:
            # We require intervals to be chronological. EDTF Date and Interval
            # both have same interface and
            # date.lower_strict() <= date.upper_strict() is always True for a
            # Date
            if e.upper_strict() < e.lower_strict():
                raise ValidationError(self._format_error(value, e))

        return value


class EDTFLevel0Validator(EDTFValidator):
    """EDTF Level 0 validator.

    python-edtf parses Level 1 and Level 2 features into subclasses of the
    Level 0 classes (e.g. ``Level2Interval`` is an ``Interval``), so this
    validator matches types exactly and checks the rest of the Level 0 rules.
    """

    def __call__(self, value):
        """Validate."""
        try:
            e = parse_edtf(value)
        except (TypeError, ParseException, AttributeError):
            # python-edtf can raise AttributeError on invalid input (e.g. seasons
            # or malformed months), and pyparsing can raise TypeError under
            # concurrent use (see babel-edtf parse_edtf). All of them are invalid
            # here
            raise ValidationError(self._format_error(value, None))

        if self._types and type(e) not in self._types:
            raise ValidationError(self._format_error(value, e))

        # Significant digits (e.g. 1950S2) are Level 1 or 2
        endpoints = [e.lower, e.upper] if isinstance(e, Interval) else [e]
        for d in endpoints:
            if getattr(d, "significant_digits", None):
                raise ValidationError(self._format_error(value, e))

        # babel-edtf formats through Python's datetime, which cannot represent
        # negative years or 0000
        lower, upper = e.lower_strict(), e.upper_strict()
        if not (
            dt.MINYEAR <= lower.tm_year <= dt.MAXYEAR
            and dt.MINYEAR <= upper.tm_year <= dt.MAXYEAR
        ):
            raise ValidationError(self._format_error(value, e))

        if self._chronological_interval:
            try:
                if upper < lower:
                    raise ValidationError(self._format_error(value, e))
            except TypeError:
                # Open bounds are compared as floats
                raise ValidationError(self._format_error(value, e))

        return value


class EDTFDateString(fields.Str):
    """
    Extended Date Format Level 0 date string field.

    A string field which is using the EDTF Validator.
    """

    def __init__(self, **kwargs):
        """Constructor."""
        kwargs.setdefault("validate", EDTFLevel0Validator(types=[Date, Interval]))
        super().__init__(**kwargs)


class EDTFDateTimeString(fields.Str):
    """
    Extended Date(/Time) Format Level 0 date string field.

    A string field which is using the EDTF Validator.
    """

    def __init__(self, **kwargs):
        """Constructor."""
        kwargs.setdefault("validate", EDTFLevel0Validator())
        super().__init__(**kwargs)


class EDTFLevel2DateString(fields.Str):
    """
    Extended Date Format Level 2 date string field.

    A string field which is using the EDTF Validator.
    """

    def __init__(self, **kwargs):
        """Constructor."""
        kwargs.setdefault(
            "validate",
            EDTFValidator(
                types=[
                    Date,
                    Interval,
                    Level1Interval,
                    UncertainOrApproximate,
                    OneOfASet,
                    Level2Interval,
                ]
            ),
        )
        super().__init__(**kwargs)
