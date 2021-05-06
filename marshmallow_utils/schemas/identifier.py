# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Persistent identifier Schema with automatic scheme detection.

Integrates idutils library to detect the scheme.
"""

import idutils
from marshmallow import Schema, ValidationError, post_load, pre_load, \
    validates_schema

from ..fields import SanitizedUnicode


class IdentifierSchema(Schema):
    """Identifier with automatic scheme detection."""

    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()

    def __init__(self, allowed_schemes, identifier_required=True, **kwargs):
        """Constructor.

        :param allowed_schemes: a list of allowed schemes. Accepts a string
            or a tuple. If IDUtils cannot validate it, it expects a tuple
            with (scheme_name, validation_function).
        :param identifier_required: True when the identifier value is required.
        """
        self.identifier_required = identifier_required

        if not allowed_schemes:
            raise ValidationError(
                    "allowed_schemes must be a list of string(s) " +
                    "and/or tuple(s)")

        self.allowed_schemes = {}
        for scheme in allowed_schemes:
            # if it is a string it should be present in IDUtils
            if isinstance(scheme, str):
                try:
                    scheme = scheme.lower()
                    val_func = getattr(idutils, f"is_{scheme}")
                    self.allowed_schemes[scheme] = val_func
                except AttributeError:
                    raise ValidationError(
                        f"Validation function for scheme {scheme} not " +
                        "found. Please provide one.")
            # tuple, (scheme, validation_function)
            elif isinstance(scheme, tuple):
                self.allowed_schemes[scheme[0].lower()] = scheme[1]
            else:
                raise ValidationError(
                    "allowed_schemes must be a list of string(s) " +
                    "and/or tuple(s)")

        super().__init__(**kwargs)

    def _intersect_with_order(self, detected_schemes):
        """Returns the first detected scheme that is allowed."""
        allowed_schemes = set(self.allowed_schemes.keys())
        for detected in detected_schemes:
            if detected in allowed_schemes:
                return detected

        return None

    @pre_load(pass_many=False)
    def load_scheme(self, data, **kwargs):
        """Loads the schema of the identifier."""
        identifier = data.get("identifier")
        if not identifier:
            return data

        scheme = data.get("scheme")
        if not scheme:
            detected_schemes = idutils.detect_identifier_schemes(identifier)
        else:
            # if given, use it
            detected_schemes = [scheme.lower()]

        # check if given or any detected is allowed
        data["scheme"] = self._intersect_with_order(detected_schemes)

        if not data["scheme"]:
            # no match between detected and allowed
            # will fail at validation step
            data.pop("scheme", None)

        return data

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        """Validate the identifier format and scheme."""
        identifier = data.get("identifier")
        scheme = data.get("scheme")

        if self.identifier_required and not identifier:
            raise ValidationError("Missing required identifier.")

        if identifier and not scheme:
            raise ValidationError(
                f"Missing or invalid scheme for identifier {identifier}."
            )

        if identifier:
            # at this point, `scheme` is set or validation failed earlier
            validation_function = self.allowed_schemes[scheme]
            if not validation_function(identifier):
                raise ValidationError(
                    f"Invalid value {identifier} for scheme {scheme}."
                )

    @post_load
    def normalize_identifier(self, data, **kwargs):
        """Normalizes the identifier based on the scheme."""
        identifier = data.get("identifier")

        # It can be empty if not required
        if identifier:
            # at this point, `scheme` is set or validation failed earlier
            scheme = data["scheme"]
            # will return the same value if not able to normalize by idutils
            data["identifier"] = idutils.normalize_pid(identifier, scheme)

        return data
