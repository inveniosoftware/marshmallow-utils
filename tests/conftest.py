# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import pytest
from marshmallow import Schema, fields

from marshmallow_utils.permissions import FieldPermissionsMixin


class TestSchema(Schema, FieldPermissionsMixin):
    """Test schema with field permissions."""

    field_dump_permissions = {
        "name": "read",
        "last_name": "read",
        "age": "read",
        "address": "manage",
    }

    name = fields.String()
    last_name = fields.String()
    age = fields.Integer()
    address = fields.String()


class Test:
    """Test class."""

    def __init__(self, name, last_name, age, address):
        """Constructor."""
        self.name = name
        self.last_name = last_name
        self.age = age
        self.address = address


@pytest.fixture()
def test_schema():
    """Fixture to return the TestSchema class."""
    return TestSchema


@pytest.fixture()
def test_object():
    """Returns a simple test object."""
    return Test("John", "Doe", 30, "CERN")


@pytest.fixture()
def test_object2():
    """Returns a simple test object."""
    return Test("Foo", "Bar", 40, "CERN")
