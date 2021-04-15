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

    def __init__(self, allowed=None, forbidden=None,
                 required=True, unknown_schemas_accepted=False, **kwargs):
        """Constructor.

        `allowed` is incompatible with `forbidden`.
        If `forbidden` has been defined (as not null),
        `allowed` will be set to null.
        If `unknown_schemas_accepted` is set to `True` all of the schemes
        not in `allowed` will be also accepted.

        The `required` param applies to the `identifier` value.
        """
        self.forbidden = forbidden
        self.allowed = None if forbidden else allowed
        self.required = required
        self.unknown_schemas_accepted = unknown_schemas_accepted

        super().__init__(**kwargs)

    def _detect_scheme(self, identifier):
        """Detect the scheme of a given identifier."""
        detected_schemes = idutils.detect_identifier_schemes(identifier)

        for d in detected_schemes:
            if d in self.allowed:
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
            # NOTE: This is required to pass PEP-8
            condition_invalid = scheme not in detected_schemes and \
                not self.unknown_schemas_accepted
            if condition_invalid:
                raise ValidationError(f"Invalid identifier format or scheme.")

            # Check if scheme is allowed
            condition_allowed = self.forbidden is None and \
                self.allowed is not None and \
                scheme not in self.allowed
            if condition_allowed:
                raise ValidationError("Scheme not allowed. Must be "
                                      f"one of {self.allowed}.")

            # Check if scheme is not allowed
            condition_forbidden = self.allowed is None and \
                self.forbidden is not None and \
                scheme in self.forbidden
            if condition_forbidden:
                raise ValidationError("Scheme disallowed. Must not be "
                                      f"one of {self.forbidden}.")

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
