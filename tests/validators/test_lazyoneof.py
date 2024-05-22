# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2024 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test LazyOneOf validator."""

import pytest
from marshmallow import Schema, ValidationError, fields

from marshmallow_utils.validators import LazyOneOf


def _get_choices():
    _get_choices.has_run = True
    return ["foo", "bar", "baz"]


def _get_labels():
    _get_labels.has_run = True
    return ["Foo", "Bar", "Baz"]


class MySchema(Schema):
    """Test schema ."""

    lazy_choices = fields.Str(
        validate=LazyOneOf(
            choices=_get_choices,
            labels=_get_labels,
            error="Must be one of: {choices} ({labels})",
        )
    )


def test_lazyoneof():
    """Test lazy one of validator."""
    # NOTE: Poor-man's mocks
    _get_choices.has_run = False
    _get_labels.has_run = False

    assert _get_choices.has_run is False
    assert _get_labels.has_run is False
    # Initialize the schema
    schema = MySchema()

    # Check that the choices and labels have still not been called
    assert _get_choices.has_run is False
    assert _get_labels.has_run is False

    assert schema.load({"lazy_choices": "foo"}) == {"lazy_choices": "foo"}

    # Check that the choices have been called
    assert _get_choices.has_run is True
    # Labels didn't need to be called
    assert _get_labels.has_run is False


def test_lazyoneof_error():
    """Test lazy one of validator errors."""
    # NOTE: Poor-man's mocks
    _get_choices.has_run = False
    _get_labels.has_run = False

    assert _get_choices.has_run is False
    assert _get_labels.has_run is False
    # Initialize the schema
    schema = MySchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({"lazy_choices": "invalid"})

    # Check that both choices and labels have been called
    assert _get_choices.has_run is True
    assert _get_labels.has_run is True

    assert exc_info.value.messages == {
        "lazy_choices": ["Must be one of: foo, bar, baz (Foo, Bar, Baz)"]
    }
