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

    def __init__(self, allowed_schemes=None, allow_all=False,
                 required=True, **kwargs):
        """Constructor.

        `allowed_schemas` is incompatible with `allow_all`.
        If `allow_all` is set to `True` the `allowed_schemes` will ignored.

        The `required` param applies to the `identifier` value.
        """
        self.allow_all = allow_all
        self.allowed_schemes = None if allow_all else allowed_schemes
        self.required = required
        super().__init__(**kwargs)

    def _detect_scheme(self, identifier):
        """Detect the scheme of a given identifier."""
        detected_schemes = idutils.detect_identifier_schemes(identifier)

        if self.allow_all:
            return detected_schemes[0] if detected_schemes else None

        for d in detected_schemes:
            if d in self.allowed_schemes:
                return d

        return None

    @pre_load(pass_many=False)
    def load_scheme(self, data, **kwargs):
        """Loads the schema of the identifier."""
        identifier = data.get("identifier")

        # Bail if identifier is not provided or scheme is provided.
        if not identifier or data.get("scheme"):
            return data

        scheme = self._detect_scheme(identifier)
        if scheme:
            data["scheme"] = scheme

        return data

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        """Validate the identifier format and scheme."""
        identifier = data.get("identifier")
        scheme = data.get("scheme")

        # If requried
        if not identifier and self.required:
            raise ValidationError("Missing required identifier.")

        if identifier:
            detected_schemes = idutils.detect_identifier_schemes(identifier)

            # A scheme should be present at this stage detected or provided
            if not scheme:
                raise ValidationError("Missing required scheme.")

            # Check if identifier is valid according to scheme.
            if scheme not in detected_schemes:
                raise ValidationError(f"Invalid identifier format or scheme.")

            # Check if scheme is allowed
            if not self.allow_all and scheme not in self.allowed_schemes:
                raise ValidationError("Scheme not allowed. Must be "
                                      f"one of {self.allowed_schemes}.")

    @post_load
    def normalize_identifier(self, data, **kwargs):
        """Normalizes the identifier based on the scheme."""
        identifier = data.get("identifier")

        # It can be empty if not required
        if identifier:
            # At this point scheme should exist or had failed
            scheme = data["scheme"]
            data["identifier"] = idutils.normalize_pid(identifier, scheme)

        return data
