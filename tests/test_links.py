# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test LinksStore."""

import pytest
from marshmallow import Schema
from uritemplate import URITemplate

from marshmallow_utils import fields
from marshmallow_utils.links import LinksSchema, LinksStore


def test_resolve_params():
    """Test link store resolver."""
    links = LinksStore(host="localhost")
    links_config = {
        "search": {
            "self": URITemplate("/{?params*}"),
        }
    }
    data = {
        "self": {
            "params": {
                "type": ["A", "B"],
                "sort": "newest",
                "subtype": ["1"],
                "size": 10,
            }
        }
    }
    links.add("search", data)

    links.resolve(config=links_config)

    assert (
        "https://localhost/?size=10&sort=newest&subtype=1&type=A&type=B" ==
        data["self"]
    )


def _assert_dump(schema_cls, config, expected_result, **opts):
    """Run a links dump test."""
    store = LinksStore(host="localhost", config=config, **opts)
    result = schema_cls(context={'links_store': store}).dump({})
    assert result == expected_result


@pytest.fixture()
def configs():
    """Links configurations."""
    return[
        # self key
        dict(item=dict(self=URITemplate("/1/{?pid}"))),
        # self key but different template
        dict(item=dict(self=URITemplate("/2/{?pid}"))),
        # self key doesn't exists
        dict(item=dict(noself=URITemplate("/3/{?pid}"))),
    ]


def test_links_schema(configs):
    """Test links schema."""
    # A links schema, generating parameters for the URI templates
    class TestLinksSchema(LinksSchema):
        namespace = 'item'
        self = fields.GenFunction(lambda r, ctx: {'pid': 1})

    # Test: Create links during dumping
    _assert_dump(
        TestLinksSchema, configs[0], {'self': 'https://localhost/1/?pid=1'})

    # Test: Create links with other config during dumping
    _assert_dump(
        TestLinksSchema, configs[1], {'self': 'https://localhost/2/?pid=1'})

    # Test: Remove unresolved links during dumping
    _assert_dump(TestLinksSchema, configs[2], {})

    # Test: Raise on unresolved links during dumping
    pytest.raises(
        KeyError, _assert_dump, TestLinksSchema, configs[2], {},
        ignore_missing=False
    )


def test_links_field(configs):
    """Test links field."""
    class Links(Schema):
        self = fields.GenFunction(lambda r, ctx: {'pid': 1})

    class TestSchema(Schema):
        links = fields.LinksField(Links, namespace='item')

    # Test: Create links during dumping
    _assert_dump(
        TestSchema, configs[0],
        {'links': {'self': 'https://localhost/1/?pid=1'}})

    # Test: Create links with other config during dumping
    _assert_dump(
        TestSchema, configs[1],
        {'links': {'self': 'https://localhost/2/?pid=1'}})

    # Test: Remove unresolved links during dumping
    _assert_dump(TestSchema, configs[2], {'links': {}})

    # Test: Raise on unresolved links during dumping
    pytest.raises(
        KeyError, _assert_dump, TestSchema, configs[2], None,
        ignore_missing=False
    )
