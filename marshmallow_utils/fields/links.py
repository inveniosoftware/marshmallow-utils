# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Link store and field for generating links."""

from marshmallow import fields, missing


class LinksField(fields.Field):
    """Links field."""

    # NOTE: forces serialization
    _CHECK_ATTRIBUTE = False

    def __init__(self, links_schema=None, namespace=None, **kwargs):
        """Constructor."""
        self.links_schema = links_schema
        self.namespace = namespace
        super().__init__(**kwargs)

    def _serialize(self, value, attr, obj, *args, **kwargs):
        # NOTE: We pass the full parent `obj`, since we want to make it
        # available to the links schema
        result = self.links_schema(context=self.context).dump(obj)
        # NOTE: By adding the "result" dictionary to the link store we achieve
        # that the link store holds a reference to this dictionary which we
        # also return as the result for this field. This is critically in
        # making the LinksStore.resolve() work. Because the link store holds a
        # reference, it doesn't matter where the links are injected in the
        # final record projection, because any updates made to the result
        # in the link store will automatically be available in the record
        # projection because it's the same dictionary being modified.
        self.context['links_store'].add(self.namespace, result)
        return result

    def _deserialize(self, value, attr, data, **kwargs):
        # NOTE: we don't deserialize the links, and we don't use dump_only=True
        # because that will by default raise a validation error unless you have
        # configured marshmallow to exclude unknown values.
        return missing
