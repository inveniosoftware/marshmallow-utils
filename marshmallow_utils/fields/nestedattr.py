# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

"""Nested attribute."""

from marshmallow import fields, missing


class AttributeAccessorFieldMixin:
    """Marshmallow field mixin for attribute-based serialization."""

    def get_value(self, obj, attr, accessor=None, default=missing):
        """Return the value for a given key from an object attribute."""
        attribute = getattr(self, "attribute", None)
        check_key = attr if attribute is None else attribute
        return getattr(obj, check_key, default)


class NestedAttribute(AttributeAccessorFieldMixin, fields.Nested):
    """Nested object attribute field."""
