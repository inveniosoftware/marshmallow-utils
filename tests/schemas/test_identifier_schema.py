# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for marshmallow Identifiers schema."""


import pytest
from marshmallow import ValidationError
from marshmallow.fields import Str

from marshmallow_utils.schemas import IdentifierSchema

# Test cases when identifier provided:
#
# scheme | detected scheme | constructor params        | success/error
#            (identifier)
# -------| -----------     | ------------------------- | -
# orcid  | orcid           |                           | passed
# orcid  | isbn            |                           | error
# orcid  | foo             |                           | error
#   -    | orcid           |                           | passed (scheme=orcid)
#   -    | foo             |                           | error
# orcid  | orcid           | allowed = [orcid]         | passed
# orcid  | orcid           | allowed = [isbn]          | error
# bar    | [isbn,orcid]    | allowed = [orcid]         | passed (scheme=orcid)
# orcid  | orcid           | forbidden = [orcid]       | error
# orcid  | orcid           | allowed = [orcid] \       | error
#                                forbidden = [orcid]
# orcid  | orcid           | allowed = [foo] \         | error
#                                forbidden = [isbn]
# orcid  | orcid           | forbidden = [isbn]        | passed
# bar    | foo             | fail_on_unknown = False   | passed


def test_no_identifier_but_required_should_fail():
    schema = IdentifierSchema()
    with pytest.raises(ValidationError):
        schema.load({})


def test_no_scheme_no_identifier_not_required_should_pass():
    schema = IdentifierSchema(identifier_required=False)
    data = schema.load({})
    assert data == {}


def test_schema_no_identifier_but_required_should_fail():
    only_scheme = {"scheme": "orcid"}
    schema = IdentifierSchema()
    with pytest.raises(ValidationError):
        schema.load(only_scheme)

    only_scheme = {"identifier": "", "scheme": "orcid"}
    with pytest.raises(ValidationError):
        schema.load(only_scheme)


def test_scheme_and_identifier_match_should_pass():
    valid_scheme_identifier = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid",
    }

    schema = IdentifierSchema()
    data = schema.load(valid_scheme_identifier)
    # NOTE: Since the schemas return the dict itself, the loaded object
    # is the same than the input and dumped objects (dicts)
    assert valid_scheme_identifier == data == schema.dump(data)


def test_scheme_and_identifier_no_match_should_pass():
    wrong_scheme = {"identifier": "0000-0001-6759-6273", "scheme": "isbn"}

    schema = IdentifierSchema()
    data = schema.load(wrong_scheme)

    correct_scheme = {"scheme": "orcid"}
    correct_scheme.update(wrong_scheme)
    assert correct_scheme == data == schema.dump(data)


def test_only_identifier_should_pass():
    only_identifier = {
        "identifier": "0000-0001-6759-6273",
    }

    schema = IdentifierSchema()
    data = schema.load(only_identifier)

    with_scheme = {"scheme": "orcid"}
    with_scheme.update(only_identifier)
    assert with_scheme == data == schema.dump(data)


def test_only_unknown_identifier_should_fail():
    only_unknown_identifier = {
        "identifier": "foobar",
    }

    schema = IdentifierSchema()
    with pytest.raises(ValidationError):
        schema.load(only_unknown_identifier)


def test_valid_scheme_identifier_allowed_should_pass():
    valid_scheme_identifier = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid",
    }

    schema = IdentifierSchema(allowed_schemes=["orcid"])
    data = schema.load(valid_scheme_identifier)
    assert valid_scheme_identifier == data == schema.dump(data)


def test_valid_scheme_identifier_not_allowed_should_fail():
    valid_scheme_identifier = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid",
    }

    schema = IdentifierSchema(allowed_schemes=["isbn"])
    with pytest.raises(ValidationError):
        schema.load(valid_scheme_identifier)


def test_invalid_scheme_detected_identifier_allowed_should_pass():
    invalid_scheme_identifier = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "bar",
    }

    schema = IdentifierSchema(allowed_schemes=["isbn", "orcid"])
    data = schema.load(invalid_scheme_identifier)

    with_scheme = {"scheme": "orcid"}
    with_scheme.update(invalid_scheme_identifier)
    assert with_scheme == data == schema.dump(data)


def test_valid_scheme_identifier_other_forbidden_should_pass():
    valid_scheme_identifier = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid",
    }

    schema = IdentifierSchema(forbidden_schemes=["isbn"])
    data = schema.load(valid_scheme_identifier)
    assert valid_scheme_identifier == data == schema.dump(data)


def test_valid_scheme_identifier_forbidden_should_fail():
    valid_scheme_identifier = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid",
    }

    schema = IdentifierSchema(forbidden_schemes=["orcid"])
    with pytest.raises(ValidationError):
        schema.load(valid_scheme_identifier)


def test_mix_allowed_forbidden_should_fail():
    with pytest.raises(ValueError):
        IdentifierSchema(
            allowed_schemes=["orcid"], forbidden_schemes=["orcid"]
        )


def test_allow_unknown_should_pass():
    valid_scheme_identifier = {"identifier": "foo", "scheme": "bar"}

    schema = IdentifierSchema(fail_on_unknown=False)
    data = schema.load(valid_scheme_identifier)
    assert valid_scheme_identifier == data == schema.dump(data)


class CustomExtraRequiredSchema(IdentifierSchema):
    """Custom schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(**kwargs)

    extra = Str(required=True)


def test_custom_inheritance_extra_provided_should_pass():
    valid_custom = {
        "extra": "random",
        "identifier": "0000-0001-6759-6273",
    }

    loaded = CustomExtraRequiredSchema().load(valid_custom)
    assert valid_custom == loaded == CustomExtraRequiredSchema().dump(loaded)


def test_custom_inheritance_extra_not_provided_but_required_should_fail():
    invalid_custom = {}

    with pytest.raises(ValidationError):
        CustomExtraRequiredSchema().load(invalid_custom)


class CustomExtraNotRequiredSchema(IdentifierSchema):
    """Custom schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(**kwargs)

    # Not required to see the failure comes from the identifier
    extra = Str()


def test_custom_inheritance_extra_with_identifier_should_pass():
    valid_custom = {
        "extra": "random",
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid",
    }

    loaded = CustomExtraNotRequiredSchema().load(valid_custom)
    assert (
        valid_custom == loaded == CustomExtraNotRequiredSchema().dump(loaded)
    )


def test_custom_inheritance_extra_without_identifier_should_fail():
    invalid_custom = {}

    with pytest.raises(ValidationError):
        CustomExtraNotRequiredSchema().load(invalid_custom)

    invalid_custom = {
        "extra": "random",
    }

    with pytest.raises(ValidationError):
        CustomExtraNotRequiredSchema().load(invalid_custom)
