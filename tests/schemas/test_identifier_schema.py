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


def validate_other(identifier):
    """Validates a numeric identifier."""
    return identifier.isnumeric()


#
# Test cases when identifier is not provided:
#
def test_invalid_allowed_schemes():
    with pytest.raises(ValidationError):
        IdentifierSchema(allowed_schemes=[1, 2, 3])


def test_identifier_required_no_value():
    schema = IdentifierSchema(allowed_schemes=[("dummy", validate_other)])
    with pytest.raises(ValidationError):
        schema.load({})


def test_identifier_not_required_no_value():
    schema = IdentifierSchema(
        allowed_schemes=[("dummy", validate_other)],
        identifier_required=False
    )
    data = schema.load({})
    assert data == {}


def test_identifier_required_only_scheme():
    schema = IdentifierSchema(allowed_schemes=[("dummy", validate_other)])
    only_scheme = {"scheme": "orcid"}
    with pytest.raises(ValidationError):
        schema.load(only_scheme)


def test_identifier_required_empty_value():
    schema = IdentifierSchema(allowed_schemes=[("dummy", validate_other)])
    empty_identifier = {"identifier": "", "scheme": "orcid"}
    with pytest.raises(ValidationError):
        schema.load(empty_identifier)

#
# Test cases when identifier provided:
#

# This schema accepts two attributes: scheme and identifier. The use
# cases are provided in the following table, `-` means that the value
# does not apply.

# 1- The scheme is given -> is allowed (idutils) -> validate -> pass
# 2- The scheme is given -> is NOT allowed -> fail
# 3- The scheme is given -> allowed is empty -> fail
# 4- The scheme is given -> is allowed (custom)  -> validate -> pass
# 5- The scheme is NOT given -> is detected -> is allowed -> validate -> pass
# 6- The scheme is NOT given -> is detected -> is NOT allowed -> fail
# 7- The scheme is NOT given -> is detected -> allowed is empty -> fail
# 8- The scheme is NOT given -> is detected (several) -> is allowed (one of them) -> pass  # noqa
# 9- The scheme is NOT given -> is detected (several) -> is allowed (not the first) -> pass  # noqa
# 10- The scheme is NOT given -> is NOT detected -> fail

# | given  | detected |
# | scheme |  scheme  |  alllowed schemes   | given identifier | result |
# |:------:|:--------:|:-------------------:|:----------------:|:------:|
# |   DOI  |     -    |        [DOI]        | 10.12345/foo.bar |  pass  |
# |   DOI  |     -    |       [Other]       | 10.12345/foo.bar |  fail  |
# |   DOI  |     -    |         []          | 10.12345/foo.bar |  fail  |
# |  Other |     -    | [(Other, val_func)] |     123456       |  pass  |
# |    -   |   [DOI]  |        [DOI]        | 10.12345/foo.bar |  pass  |
# |    -   |   [DOI]  |       [Other]       | 10.12345/foo.bar |  fail  |
# |    -   |   [DOI]  |         []          | 10.12345/foo.bar |  fail  |
# |    -   |  [isni,  |       [isni]        |     0317-8471    |  pass  |  (scheme = isni)  # noqa
# |        |  orcid]  |                     |                  |        |
# |    -   |  [isni,  |       [orcid]       |     0317-8471    |  pass  |  (scheme = orcid)  # noqa
# |        |  orcid]  |                     |                  |        |
# |    -   |     -    |       [isni]        |    00:11:22:33   |  fail  |


def test_given_and_allowed_scheme_valid_value():  # 1
    schema = IdentifierSchema(allowed_schemes=["doi"])
    valid_doi = {
        "scheme": "doi",
        "identifier": "10.12345/foo.bar"
    }
    data = schema.load(valid_doi)
    assert data == valid_doi


def test_given_and_allowed_scheme_invalid_value():  # 1
    schema = IdentifierSchema(allowed_schemes=["doi"])
    invalid_doi = {
        "scheme": "doi",
        "identifier": "12345"
    }
    with pytest.raises(ValidationError):
        schema.load(invalid_doi)


def test_given_and_not_allowed_scheme_valid_value():  # 2
    schema = IdentifierSchema(allowed_schemes=[("other", validate_other)])
    valid_doi = {
        "scheme": "doi",
        "identifier": "10.12345/foo.bar"
    }
    with pytest.raises(ValidationError):
        schema.load(valid_doi)


def test_given_and_allowed_empty_scheme_valid_value():  # 3 and 7
    # NOTE: does not allow the instantiation with emtpy allowed schemes
    with pytest.raises(ValidationError):
        IdentifierSchema(allowed_schemes=[])


def test_given_custom_and_allowed_scheme_valid_value():  # 4
    schema = IdentifierSchema(allowed_schemes=[("other", validate_other)])
    valid_other = {
        "scheme": "Other",  # to check the normalized lowercase
        "identifier": "12345"
    }

    data = schema.load(valid_other)
    assert data == valid_other


def test_given_custom_and_allowed_scheme_invalid_value():  # 4
    schema = IdentifierSchema(allowed_schemes=[("other", validate_other)])
    invalid_other = {
        "scheme": "other",
        "identifier": "12345abc"
    }

    with pytest.raises(ValidationError):
        schema.load(invalid_other)


def test_detected_and_allowed_scheme_valid_value():  # 5
    schema = IdentifierSchema(allowed_schemes=["doi"])
    valid_doi = {
        "identifier": "10.12345/foo.bar"
    }
    data = schema.load(valid_doi)

    valid_doi["scheme"] = "doi"
    assert data == valid_doi


def test_detected_and_not_allowed_scheme_valid_value():  # 6
    schema = IdentifierSchema(allowed_schemes=[("other", validate_other)])
    valid_doi = {
        "identifier": "10.12345/foo.bar"
    }

    with pytest.raises(ValidationError):
        schema.load(valid_doi)


def test_detected_and_allowed_scheme_respect_detection_order():  # 8
    schema = IdentifierSchema(allowed_schemes=["orcid", "isni"])
    valid_orcid = {
        "identifier": "0000-0001-6759-6273"
    }
    data = schema.load(valid_orcid)

    valid_orcid["scheme"] = "orcid"
    assert data == valid_orcid


def test_detected_and_allowed_scheme_second_detected():  # 8
    schema = IdentifierSchema(allowed_schemes=["isni"])
    valid_isni = {
        "identifier": "0000-0001-6759-6273"
    }
    data = schema.load(valid_isni)

    valid_isni["scheme"] = "isni"
    assert data == valid_isni


def test_not_given_not_detected_scheme_for_identifier():  # 10
    schema = IdentifierSchema(allowed_schemes=["isni"])
    invalid_no_scheme = {
        "identifier": "00:11:22:33"
    }

    with pytest.raises(ValidationError):
        schema.load(invalid_no_scheme)
