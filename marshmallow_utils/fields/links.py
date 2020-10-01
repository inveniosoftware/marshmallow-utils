# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Link store and field for generating links."""

from marshmallow import fields, missing


class Links(fields.Field):
    """A links field that knows to look in the context for the schema."""

    # NOTE: forces serialization
    _CHECK_ATTRIBUTE = False

    def _serialize(self, value, attr, obj, *args, **kwargs):
        """Dump the field by using the contextual schema."""
        factory = self.context.get("links_factory") or {}
        namespace = self.context.get("links_namespace", {})
        schema = factory.get_schema(namespace, self.context)
        if schema:
            return schema.dump(obj)
        else:
            return {}


class Link(fields.Field):
    """A link field that knows how to generate a link from an object."""

    # NOTE: forces serialization
    _CHECK_ATTRIBUTE = False

    def __init__(self, template=None, params=None, permission=None, **kwargs):
        """Constructor."""
        self.template = template
        self.permission = permission
        self.params = params
        super().__init__(**kwargs)

    def _serialize(self, value, attr, obj, *args, **kwargs):
        """Dump the link by using the context."""
        factory = self.context.get("links_factory")
        field_permission_check = self.context.get("field_permission_check")

        if field_permission_check and self.permission:
            if not field_permission_check(self.permission):
                return missing
        return factory.create_link(self.template, self.params(obj))
