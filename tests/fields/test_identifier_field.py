# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for marshmallow Identifiers field."""

from functools import partial

import pytest
from marshmallow import Schema, ValidationError
from marshmallow.fields import Nested

from marshmallow_utils.fields import IdentifierSet
from marshmallow_utils.schemas import IdentifierSchema


class TestSchema(Schema):
    identifiers = IdentifierSet(
        Nested(
            partial(IdentifierSchema, allowed_schemes=["doi", "orcid"])
        )
    )


def test_valid_identifiers():
    valid_identifiers = {
        "identifiers": [{
            "identifier": "0000-0001-6759-6273",
            "scheme": "orcid"
            }, {
            "identifier": "10.5281/zenodo.9999999",
            "scheme": "doi"
        }]
    }

    assert TestSchema().load(valid_identifiers) == valid_identifiers


def test_invalid_duplicate_identifiers():
    duplicate_identifiers = {
        "identifiers": [{
            "identifier": "10.5281/zenodo.9999999",
            "scheme": "doi"
            }, {
            "identifier": "10.5281/zenodo.9999999",
            "scheme": "doi"
        }]
    }

    with pytest.raises(ValidationError) as excinfo:
        TestSchema().load(duplicate_identifiers)


def test_invalid_duplicate_identifiers_no_scheme_provided():
    duplicate_identifiers = {
        "identifiers": [{
            "identifier": "10.5281/zenodo.9999999",
            }, {
            "identifier": "10.5281/zenodo.9999999",
        }]
    }

    with pytest.raises(ValidationError) as excinfo:
        TestSchema().load(duplicate_identifiers)


def test_invalid_empty_identifiers():
    duplicate_identifiers = {
        "identifiers": [{}]
    }

    with pytest.raises(ValidationError) as excinfo:
        TestSchema().load(duplicate_identifiers)
