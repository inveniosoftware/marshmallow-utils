# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identifier field."""

from marshmallow.fields import List


class IdentifierSet(List):
    """Identifier list with deduplication.

    It assumes the items of the list contain a *scheme* property.
    """

    default_error_messages = {
        "multiple_values": "Only one identifier per scheme is allowed.",
    }

    def _validate(self, value):
        """Validates the list of identifiers."""
        schemes = [identifier["scheme"] for identifier in value]
        if len(value) != len(set(schemes)):
            raise self.make_error(key="multiple_values")


class IdentifierValueSet(List):
    """Identifier list with deduplication.

    It assumes the items of the list contain a *scheme* property.
    """

    default_error_messages = {
        "multiple_values": "Duplicated identifier entry is not allowed.",
    }

    def _validate(self, value):
        """Validates the list of identifiers."""
        identifiers = [
            (identifier["scheme"], identifier["identifier"]) for identifier in value
        ]
        if len(value) != len(set(identifiers)):
            raise self.make_error(key="multiple_values")
