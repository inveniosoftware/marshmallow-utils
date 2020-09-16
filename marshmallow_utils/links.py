# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Link store and field for generating links."""

from collections import defaultdict

from marshmallow import fields, missing


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
        for ns, link_objects in self._links.items():
            if ns not in config:
                raise Exception(f'Unknown links namespace: {ns}')
            for links in link_objects:
                for k, v in links.items():
                    links[k] = self.base_url(
                        host=self.host,
                        path=config[ns][k].expand(**context, **v),
                        # TODO: how do we handle this via URITemplate?
                        # querystring='...',
                    )

    @staticmethod
    def base_url(scheme="https", host=None, path="/", querystring="",
                 api=False):
        """Creates the URL for API and UI endpoints."""
        assert path.startswith("/")
        path = f"/api{path}" if api else path
        return f"{scheme}://{host}{path}{querystring}"
