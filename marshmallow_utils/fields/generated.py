# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Generated field."""






from .contrib import Function, Method


class GeneratedValue:
    """Sentinel value class forcing marshmallow missing field generation."""


class ForcedFieldDeserializeMixin:
    """Mixin that forces deserialization of marshmallow fields."""

    # Overriding default deserializer since we need to deserialize an
    # initially non-existent field. In this implementation the checks are
    # removed since we expect our deserializer to provide the value.
    def deserialize(self, *args, **kwargs):
        """Deserialize field."""
        # Proceed with _deserialization, skipping all checks.
        output = self._deserialize(*args, **kwargs)
        self._validate(output)
        return output


class GenFunction(ForcedFieldDeserializeMixin, Function):
    """Function field which is always deserialized."""


class GenMethod(ForcedFieldDeserializeMixin, Method):
    """Method field which is always deserialized."""
