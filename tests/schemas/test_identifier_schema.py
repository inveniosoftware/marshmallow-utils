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


def test_full_identifier():
    valid_full = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid"
    }

    schema = IdentifierSchema(allowed=["orcid", "ror"])
    loaded = schema.load(valid_full)
    # NOTE: Since the schemas return the dict itself, the loaded object
    # is the same than the input and dumped objects (dicts)
    assert valid_full == loaded == schema.dump(loaded)


def test_identifier_auto_scheme():
    valid_identifier = {
        "identifier": "0000-0001-6759-6273",
    }

    schema = IdentifierSchema(allowed=["orcid"])
    loaded = schema.load(valid_identifier)
    # NOTE: Since the schemas return the dict itself, the loaded object
    # is the same than the input and dumped objects (dicts)
    valid_identifier["scheme"] == "orcid"
    assert valid_identifier == loaded == schema.dump(loaded)


def test_identifier_not_provided():
    invalid_no_identifier = {
        "scheme": "orcid"
    }

    schema = IdentifierSchema(allowed=["orcid"])

    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_no_identifier)


def test_blank_identifier():
    invalid_blank_identifier = {
        "identifier": "",
        "scheme": "orcid"
    }

    schema = IdentifierSchema(allowed=["orcid"])
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_blank_identifier)


def test_invalid_identifier():
    invalid_blank_identifier = {
        "identifier": "inv",
        "scheme": "orcid"
    }

    schema = IdentifierSchema(allowed=["orcid"])
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_blank_identifier)


def test_autoschema_not_allowed():
    invalid_identifier = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid"
    }

    schema = IdentifierSchema(allowed=["ror"])
    with pytest.raises(ValidationError):
        schema.load(invalid_identifier)


def test_invalid_scheme_or_format():
    invalid_identifier = {
        "identifier": "0000-0000-0000-00000000",
        "scheme": "provided-scheme"
    }

    schema = IdentifierSchema(allowed=["provided-scheme"])
    with pytest.raises(ValidationError) as excinfo:
        loaded = schema.load(invalid_identifier)


def test_autoschema_not_recognized():
    invalid_identifier = {
        "identifier": "0000-0000-0000-00000000",
    }

    schema = IdentifierSchema(allowed=["orcid"])
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_identifier)


def test_identifier_not_required():
    """When the provided schema is allowed but different format."""
    valid_identifier = {}

    schema = IdentifierSchema(allowed=["orcid"], required=False)
    loaded = schema.load(valid_identifier)
    assert valid_identifier == loaded == schema.dump(loaded)

    # Scheme is ignored since there is no identifier value
    valid_identifier = {"scheme": "isni"}

    loaded = schema.load(valid_identifier)
    assert valid_identifier == loaded == schema.dump(loaded)


def test_full_identifier_not_required():
    valid_full = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid"
    }

    schema = IdentifierSchema(allowed=["orcid"], required=False)
    loaded = schema.load(valid_full)
    # NOTE: Since the schemas return the dict itself, the loaded object
    # is the same than the input and dumped objects (dicts)
    assert valid_full == loaded == schema.dump(loaded)


def test_identifier_auto_scheme_not_required():
    valid_identifier = {
        "identifier": "0000-0001-6759-6273",
    }

    schema = IdentifierSchema(allowed=["orcid"], required=False)
    loaded = schema.load(valid_identifier)
    # NOTE: Since the schemas return the dict itself, the loaded object
    # is the same than the input and dumped objects (dicts)
    valid_identifier["scheme"] == "orcid"
    assert valid_identifier == loaded == schema.dump(loaded)


class CustomNotRequiredSchema(IdentifierSchema):
    """License schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(required=False, **kwargs)

    extra = Str(required=True)


def test_custom_inheritance_not_required():
    valid_custom = {
        "extra": "random",
    }

    loaded = CustomNotRequiredSchema().load(valid_custom)
    assert valid_custom == loaded == CustomNotRequiredSchema().dump(loaded)


def test_invalid_custom_inheritance_not_required():
    invalid_custom = {}

    with pytest.raises(ValidationError) as excinfo:
        loaded = CustomNotRequiredSchema().load(invalid_custom)


class CustomRequiredSchema(IdentifierSchema):
    """License schema."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(**kwargs)

    # Not required to see the failure comes form the identifier
    extra = Str()


def test_custom_inheritance_not_required():
    valid_custom = {
        "extra": "random",
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid"
    }

    loaded = CustomRequiredSchema().load(valid_custom)
    assert valid_custom == loaded == CustomRequiredSchema().dump(loaded)


def test_invalid_custom_inheritance_not_required():
    invalid_custom = {}

    with pytest.raises(ValidationError) as excinfo:
        loaded = CustomRequiredSchema().load(invalid_custom)

    invalid_custom = {
        "extra": "random",
    }

    with pytest.raises(ValidationError) as excinfo:
        loaded = CustomRequiredSchema().load(invalid_custom)


def test_unknown_schema_accepting_unknown():
    unknown_schema = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "provided-scheme"
    }

    schema = IdentifierSchema(unknown_schemas_accepted=True,
                              allowed=['provided-scheme'])
    loaded = schema.load(unknown_schema)
    assert unknown_schema == loaded == schema.dump(loaded)


def test_unknown_schema_not_accepting_unknown():
    unknown_schema = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "provided-scheme"
    }

    with pytest.raises(ValidationError) as excinfo:
        loaded = IdentifierSchema().load(unknown_schema)


def test_not_forbidden_schema():
    valid_full = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid"
    }

    schema = IdentifierSchema()
    loaded = schema.load(valid_full)

    assert valid_full == loaded == schema.dump(loaded)


def test_forbidden_schema():
    valid_full = {
        "identifier": "0000-0001-6759-6273",
        "scheme": "orcid"
    }

    with pytest.raises(ValidationError) as excinfo:
        loaded = IdentifierSchema(forbidden=["orcid", "ror"]).load(valid_full)
