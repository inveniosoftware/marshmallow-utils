# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test LinksStore."""


from uritemplate import URITemplate

from marshmallow_utils.links import LinksStore


def test_resolve_params():
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
