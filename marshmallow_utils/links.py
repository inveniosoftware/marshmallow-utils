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
from werkzeug.datastructures import MultiDict


def _unpack_dict(data):
    """Unpack lists inside a dict.

    For instance this dictionary:

    .. code-block:: python

        {
            "type": ["A", "B"],
            "sort": "newest",
        }

    Is expanded to:

    .. code-block:: python

        [
            ("sort", "newest"),
            ("type", "A"),
            ("type", "B"),
        ]
    """
    for key, value in sorted(data.items()):
        if isinstance(value, list):
            for v in value:
                yield key, v
        else:
            yield key, value


class LinksStore:
    """Utility class for keeping track of and resolve links.

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

    If the ``config`` is provided in the constructor, links will be resolved
    immediately. If no config is provided, the links will be resolved upon a
    call to ``resolve()`` method with the config.

    :params host: A hostname or a callable returning a hostname.
    :params config: A link configuration/
    :params context: Extra template variables.
    :params ignore_missing: If true, missing templates will be ignored.
    """

    def __init__(self, host=None, config=None, context=None,
                 ignore_missing=True):
        """Constructor."""
        self._host = host
        self.config = config
        self._links = defaultdict(list)
        self._context = context or {}
        self._ignore_missing = ignore_missing

    def add(self, namespace, links):
        """Adds a dictionary of links under a namespace."""
        self._links[namespace].append(links)
        if self.config:
            self.resolve()

    @property
    def host(self):
        """Get the hostname."""
        return self._host() if callable(self._host) else self._host

    # TODO: Deprecate
    def resolve(self, config=None, context=None):
        """Resolves in-place all the tracked link dictionaries."""
        config = config or self.config
        context = context or self._context
        assert config, "Links config is empty."

        # Iterate over all namespaces
        for namespace, links_objects in self._links.items():
            if namespace not in config:
                raise Exception(f'Unknown links namespace: {namespace}')

            # For each namespace, iterate over the list of link dicts
            for links in links_objects:

                # Resolve all links in the link dict.
                rmkeys = []
                for link_key, link_params in links.items():
                    try:
                        template = config[namespace][link_key]
                        links[link_key] = self.expand_link(
                            template, {**context, **link_params})
                    except KeyError:
                        # no template found - ignore or raise
                        if self._ignore_missing:
                            rmkeys.append(link_key)
                        else:
                            raise

                # Remove keys that wasn't rendered
                for k in rmkeys:
                    del links[k]

    def expand_link(self, template, vars):
        """Expand the link template with the template variables.

        :param template: URITemplate to expand.
        :param vars: The template variables for the expansion.
        """
        return self.base_url(
            host=self.host,
            rendered_path=template.expand(**self.preprocess_vars(vars))
        )

    @staticmethod
    def preprocess_vars(vars):
        """Preprocess template variables before expansion."""
        for k, v in vars.items():
            if isinstance(v, MultiDict):
                vars[k] = list(sorted(v.items(multi=True)))
            elif isinstance(v, dict):
                # Note, we unpack dicts with list values at this level, because
                # there are no meaningful templates that can make use of them
                # (basically the lists just becomes URL encoded python objects)
                vars[k] = list(_unpack_dict(v))
        return vars

    @staticmethod
    def base_url(scheme="https", host=None, rendered_path="/"):
        """Creates the URL for API and UI endpoints."""
        if host and scheme:
            assert rendered_path.startswith("/")
            return f"{scheme}://{host}{rendered_path}"
        else:
            return rendered_path


# TODO: Deprecate
class LinksSchema(Schema):
    """Links schema that stores the result in a link store."""

    namespace = None

    @post_dump()
    def _store(self, data, **kwargs):
        self.context["links_store"].add(self.namespace, data)
        if "links_config" in self.context:
            self.context["links_store"].resolve(
                config=self.context["links_config"])
        return data
