# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for marshmallow schema post dump permissions check."""


def mocked_field_permission_check(action, identity=None, **kwargs):
    """Mocked permission resolution."""
    mocked_field_permission_check.counter += 1
    if action == "read":
        return True
    elif action == "manage":
        return False

    return False


def mocked_field_permission_check_allow_manage(action, identity=None, **kwargs):
    """Mocked permission resolution allowing to manage."""
    mocked_field_permission_check.counter += 1
    if action == "read":
        return True
    elif action == "manage":
        return True

    return False


def test_post_dump_permissions_removal(test_schema, test_object, test_object2):
    """Test that some fields are removed based on the permissions level access of the user."""
    mocked_field_permission_check.counter = 0  # We count the number of times the function is called because we are caching the return value in "_permissions_filter_dump" to increase the performance

    test = test_schema(
        context={"field_permission_check": mocked_field_permission_check}
    ).dump(test_object)

    assert test["name"] == "John"
    assert test["last_name"] == "Doe"
    assert test["age"] == 30
    assert not test.get("address")

    assert (
        mocked_field_permission_check.counter == 2
    )  # since only 2 different permissions are defined in the attribute "field_dump_permissions" of the schema, we should only resolve 2 times the permissions

    mocked_field_permission_check.counter = 0  # We reset the counter

    test = test_schema(
        context={"field_permission_check": mocked_field_permission_check_allow_manage}
    ).dump([test_object, test_object2], many=True)

    assert len(test) == 2

    # Now it simulates that the permission check logic allows us to see all the fields
    assert test[0]["name"] == "John"
    assert test[0]["last_name"] == "Doe"
    assert test[0]["age"] == 30
    assert test[0].get("address") == "CERN"

    assert test[1]["name"] == "Foo"
    assert test[1]["last_name"] == "Bar"
    assert test[1]["age"] == 40
    assert test[1].get("address") == "CERN"

    assert (
        mocked_field_permission_check.counter == 4
    )  # since only 2 different permissions are defined in the attribute "field_dump_permissions" of the schema, we should only resolve 4 times the permissions (2 permissions checks * 2 different records)
