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

    error_messages = {
        "invalid_identifier": "Invalid {scheme} identifier.",
        "invalid_scheme": "Invalid scheme.",
        "required": "Missing data for required field.",
    }

    def __init__(self, allowed_schemes, identifier_required=True, **kwargs):
        """Constructor.

        :param allowed_schemes: a dictionary of allowed schemes. Each key must
            contain a validator function and a scheme label.
        :param identifier_required: True when the identifier value is required.
        """
        self.identifier_required = identifier_required
        self.allowed_schemes = allowed_schemes
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
        detected_scheme = self._intersect_with_order(detected_schemes)

        if detected_scheme:
            # no match between detected and allowed
            # will fail at validation step
            data["scheme"] = detected_scheme

        return data

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        """Validate the identifier format and scheme."""
        identifier = data.get("identifier")
        scheme = data.get("scheme")

        errors = dict()
        if not scheme:
            errors['scheme'] = self.error_messages["required"]
        elif scheme not in self.allowed_schemes:
            errors['scheme'] = self.error_messages[
                "invalid_scheme"
            ].format(scheme=scheme)

        if self.identifier_required and not identifier:
            errors['identifier'] = self.error_messages["required"]

        if identifier and scheme and scheme in self.allowed_schemes:
            validation_function = self.allowed_schemes[scheme]["validator"]
            if not validation_function(identifier):
                scheme_label = self.allowed_schemes[scheme].get(
                    "label", scheme
                )
                message = self.error_messages["invalid_identifier"]
                errors['identifier'] = message.format(scheme=scheme_label)

        if errors:
            raise ValidationError(errors)

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
