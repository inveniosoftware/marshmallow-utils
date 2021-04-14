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

    def __init__(
        self,
        allowed_schemes=None,
        forbidden_schemes=None,
        fail_on_unknown=True,
        identifier_required=True,
        **kwargs,
    ):
        """Constructor.

        :param allowed_schemes: allowed schemes or None if any allowed.
        :param forbidden_schemes: forbidden schemes or None if any allowed.
            Takes precedence over `allowed_schemes`.
        :param fail_on_unknown: fail when the scheme of the identifier is not
            one of the detected schemes with idutils.
        :param identifier_required: True when the identifier value is required.
        """
        if allowed_schemes and forbidden_schemes:
            raise ValueError(
                "Bad arguments allowed_schemea and forbidden_schemes: "
                "only one allowed."
            )

        self.forbidden_schemes = forbidden_schemes or set()
        if forbidden_schemes:
            self.allowed_schemes = set()
        else:
            self.allowed_schemes = allowed_schemes or set()
        self.fail_on_unknown = fail_on_unknown
        self.identifier_required = identifier_required

        super().__init__(**kwargs)

    def _detect_scheme(self, identifier):
        """Detect and return the scheme of a given identifier."""
        detected_schemes = idutils.detect_identifier_schemes(identifier)

        # force setting the scheme to one of the detected when
        # allowed_schemes list is provided
        if self.allowed_schemes:
            for d in detected_schemes:
                if d in self.allowed_schemes:
                    return d

        first_or_none = detected_schemes[0] if detected_schemes else None
        return first_or_none

    @pre_load(pass_many=False)
    def load_scheme(self, data, **kwargs):
        """Loads the schema of the identifier."""
        identifier = data.get("identifier")
        if not identifier:
            return data

        # override any provided scheme if detected
        scheme = self._detect_scheme(identifier)
        if scheme:
            data["scheme"] = scheme

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
                f"Missing scheme value for identifier {identifier}."
            )

        if identifier:
            # at this point, `scheme` is set or validation failed earlier
            detected_schemes = idutils.detect_identifier_schemes(identifier)

            is_forbidden = scheme in self.forbidden_schemes
            if is_forbidden:
                raise ValidationError(f"Invalid scheme {scheme}.")

            is_not_allowed = (
                self.allowed_schemes and scheme not in self.allowed_schemes
            )
            if is_not_allowed:
                raise ValidationError(f"Invalid scheme {scheme}.")

            unknown = scheme not in detected_schemes
            if unknown and self.fail_on_unknown:
                raise ValidationError(f"Invalid scheme {scheme}.")

    @post_load
    def normalize_identifier(self, data, **kwargs):
        """Normalizes the identifier based on the scheme."""
        identifier = data.get("identifier")

        # It can be empty if not required
        if identifier:
            # at this point, `scheme` is set or validation failed earlier
            scheme = data["scheme"]
            data["identifier"] = idutils.normalize_pid(identifier, scheme)

        return data
