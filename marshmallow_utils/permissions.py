# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2025-2026 Graz University of Technology.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Field-level permissions."""

from warnings import warn

from marshmallow import post_dump, pre_load

from .context import context_schema


class FieldPermissionError(Exception):
    """Marshmallow field permission error."""


class FieldPermissionsMixin:
    """Mixin for filtering field-level permissions in marshmallow schemas."""

    field_load_permissions = {}
    field_dump_permissions = {}
    default_load_action = None
    default_dump_action = None

    @pre_load
    def _permissions_filter_load(self, data, **kwargs):
        if "field_permission_check" in self.context:
            warn(
                "using self.context for field_permission_check is deprecated, use marshmallow_utils.context:context_schema for it.",
                DeprecationWarning,
            )
            field_permission_check = self.context.get("field_permission_check")
        else:
            try:
                field_permission_check = context_schema.get()["field_permission_check"]
            except LookupError:
                field_permission_check = False

        if field_permission_check:
            for k in self.field_load_permissions:
                if k in data:
                    action = self.field_load_permissions[k] or self.default_load_action
                    # TODO (Alex): Maybe cache?
                    if action and not field_permission_check(action):
                        raise FieldPermissionError(k)
        return data

    @post_dump
    def _permissions_filter_dump(self, data, **kwargs):
        if "field_permission_check" in self.context:
            warn(
                "using self.context for field_permission_check is deprecated, use marshmallow_utils.context:context_schema for it.",
                DeprecationWarning,
            )
            field_permission_check = self.context.get("field_permission_check")
        else:
            try:
                field_permission_check = context_schema.get()["field_permission_check"]
            except LookupError:
                field_permission_check = False

        if field_permission_check:
            # Initialize permissions cache to avoid to re-compute permissions that are repeated
            _permissions_cache = dict()
            for k in self.field_dump_permissions:
                if k in data:
                    action = self.field_dump_permissions[k] or self.default_dump_action
                    has_permission = _permissions_cache.get(action)
                    if not has_permission:
                        has_permission = field_permission_check(action)
                        _permissions_cache[action] = has_permission
                    if action and not has_permission:
                        del data[k]
        return data
