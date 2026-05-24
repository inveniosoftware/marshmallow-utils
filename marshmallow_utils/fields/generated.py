# SPDX-FileCopyrightText: 2016-2020 CERN.
# SPDX-FileCopyrightText: 2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Generated field."""

from .contrib import Function, Method


class GeneratedValue(object):
    """Sentinel value class forcing marshmallow missing field generation."""

    pass


class ForcedFieldDeserializeMixin(object):
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

    pass


class GenMethod(ForcedFieldDeserializeMixin, Method):
    """Method field which is always deserialized."""

    pass
