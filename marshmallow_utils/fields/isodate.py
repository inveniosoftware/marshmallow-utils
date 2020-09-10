# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Date string field."""

import arrow
from arrow.parser import ParserError
from marshmallow import fields, missing


class ISODateString(fields.Date):
    """ISO8601-formatted date string."""

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize an ISO8601-formatted date."""
        try:
            return super()._serialize(
                arrow.get(value).date(), attr, obj, **kwargs)
        except ParserError:
            return missing

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize an ISO8601-formatted date."""
        return super()._deserialize(value, attr, data, **kwargs).isoformat()
