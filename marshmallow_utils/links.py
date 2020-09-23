# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Link store and field for generating links."""

from collections import defaultdict

from marshmallow import Schema, fields, missing, post_dump
from uritemplate import URITemplate


class LinksStore:
    """Utility class for keeping track of links.

    The ``config`` argument is a dictionary with link namespaces as keys and a
    dictionary of link types and their URITemplate objects.

    Exmple usage:

    ..code-block:: python

        link_store = LinksStore()
        data = {
            'links': {
                'self': {'pid_value': '12345'},
                'draft': {'pid_value': '12345'},
            },
        }
        link_store.add('record', data['links'])
        link_store.resolve(config={
            'record': {
                'self': URITemplate('/api/records{/pid_value}'),
                'draft': URITemplate('/api/records{/pid_value}/draft'),
            }
        })
    """

    def __init__(self, host=None, config=None):
        """Constructor."""
        self._host = host
        self.config = config
        self._links = defaultdict(list)

    def add(self, namespace, links):
        """Adds a dictionary of links under a namespace."""
        self._links[namespace].append(links)

    @property
    def host(self):
        """Get the hostname."""
        return self._host() if callable(self._host) else self._host

    def resolve(self, context=None, config=None):
        """Resolves in-place all the tracked link dictionaries."""
        config = config or self.config
        assert config, "Links config is empty."

        context = context or {}
        parameters = self._links

        for ns, keyed_parameters_array in parameters.items():
            if ns not in config:
                raise Exception(f'Unknown links namespace: {ns}')

            # Why is this a list?
            for keyed_parameters in keyed_parameters_array:
                # Always just a list of 1 dict with
                # keys: each link key
                # values: dict with 1
                #     key: "params"
                #     value: dict of querystring parameters
                for k, params in keyed_parameters.items():
                    keyed_parameters[k] = self.to_link(
                        config[ns][k],
                        {**context, **params}
                    )

    def to_link(self, template, values):
        """Expand the link template with the values."""
        # NOTE: Querystring parameters are dealt separately because
        #       URITemplate doesn't recursively expand the 'params' dict,
        #       so we have to do it ourselves carefully
        qs_parameters = values.get("params", {})
        qs = ""
        for idx, key in enumerate(sorted(qs_parameters.keys())):
            prefix = "?" if idx == 0 else "&"
            tpl = URITemplate(f"{{{prefix}{key}*}}")
            qs_part = tpl.expand({key: qs_parameters[key]})
            qs += qs_part

        path = template.expand({**values, "params": {}})

        return self.base_url(
            host=self.host,
            path=path,
            querystring=qs
        )

    @staticmethod
    def base_url(scheme="https", host=None, path="/", querystring="",
                 api=False):
        """Creates the URL for API and UI endpoints."""
        assert path.startswith("/")
        path = f"/api{path}" if api else path
        return f"{scheme}://{host}{path}{querystring}"


class LinksSchema(Schema):
    """Links schema that stores the result in a link store."""

    namespace = None

    @post_dump()
    def _store(self, data, **kwargs):
        self.context['links_store'].add(self.namespace, data)
        return data
