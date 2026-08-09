# SPDX-FileCopyrightText: 2016-2021 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Date string field."""

import pendulum
from marshmallow import fields, missing
from pendulum.parsing import ParserError


class ISODateString(fields.Date):
    """ISO8601-formatted date string.

    ISODateString serializes to a date string and if it can't, the field is
    ignored (missing).

    NOTE: It serializes None to None.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize an ISO8601-formatted date."""
        try:
            return super()._serialize(pendulum.parse(value).date(), attr, obj, **kwargs)
        except (ParserError, ValueError, TypeError):
            # pendulum.parse() can raise a ValueError (e.g. on ""), or a TypeError (e.g. on None)
            return missing

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize an ISO8601-formatted date."""
        return super()._deserialize(value, attr, data, **kwargs).isoformat()
