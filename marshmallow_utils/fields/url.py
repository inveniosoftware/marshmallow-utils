# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2023 CERN.
# Copyright 2021 Steven Loria and contributors
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Update URL field."""

from __future__ import annotations

import re
import typing

from marshmallow import types
from marshmallow.exceptions import ValidationError
from marshmallow.fields import String
from marshmallow.validate import Validator


class URLValidator(Validator):
    """Validate a URL.

    Marshmallow's URL validator doesn't allow underscores in subdomains.
    https://github.com/marshmallow-code/marshmallow/blob/27294efc374d9a073386bb6aba807e9b7eb525f6/src/marshmallow/validate.py#L93
    This validator allows underscores in the subdomains.


    :param relative: Whether to allow relative URLs.
    :param absolute: Whether to allow absolute URLs.
    :param error: Error message to raise in case of a validation error.
        Can be interpolated with `{input}`.
    :param schemes: Valid schemes. By default, ``http``, ``https``,
        ``ftp``, and ``ftps`` are allowed.
    :param require_tld: Whether to reject non-FQDN hostnames.
    """

    class RegexMemoizer:
        """RegexMemoizer for URLValidator."""

        def __init__(self):
            """Constructor."""
            self._memoized = {}

        def _regex_generator(
            self, relative: bool, absolute: bool, require_tld: bool
        ) -> typing.Pattern:
            hostname_variants = [
                # a normal domain name, expressed in [A-Z0-9] chars with hyphens allowed only in the middle
                # note that the regex will be compiled with IGNORECASE, so these are upper and lowercase chars
                (
                    r"(?:[A-Z0-9](?!.*(-_|_-))(?:[A-Z0-9-_]{0,61}[A-Z0-9])?\.)+"
                    r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)"
                ),
                # or the special string 'localhost'
                r"localhost",
                # or IPv4
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
                # or IPv6
                r"\[[A-F0-9]*:[A-F0-9:]+\]",
            ]
            if not require_tld:
                # allow dotless hostnames
                hostname_variants.append(r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.?)")

            absolute_part = "".join(
                (
                    # scheme (e.g. 'https://', 'ftp://', etc)
                    # this is validated separately against allowed schemes, so in the regex
                    # we simply want to capture its existence
                    r"(?:[a-z0-9\.\-\+]*)://",
                    # basic_auth, for URLs encoding a username:password
                    # e.g. 'ftp://foo:bar@ftp.example.org/'
                    r"(?:[^:@]+?(:[^:@]*?)?@|)",
                    # netloc, the hostname/domain part of the URL plus the optional port
                    r"(?:",
                    "|".join(hostname_variants),
                    r")",
                    r"(?::\d+)?",
                )
            )
            relative_part = r"(?:/?|[/?]\S+)\Z"

            if relative:
                if absolute:
                    parts: tuple[str, ...] = (
                        r"^(",
                        absolute_part,
                        r")?",
                        relative_part,
                    )
                else:
                    parts = (r"^", relative_part)
            else:
                parts = (r"^", absolute_part, relative_part)

            return re.compile("".join(parts), re.IGNORECASE)

        def __call__(
            self, relative: bool, absolute: bool, require_tld: bool
        ) -> typing.Pattern:
            """Generate, memoize and return validation regex."""
            key = (relative, absolute, require_tld)
            if key not in self._memoized:
                self._memoized[key] = self._regex_generator(
                    relative, absolute, require_tld
                )

            return self._memoized[key]

    _regex = RegexMemoizer()

    default_message = "Not a valid URL."
    default_schemes = {"http", "https", "ftp", "ftps"}

    def __init__(
        self,
        *,
        relative: bool = False,
        absolute: bool = True,
        schemes: types.StrSequenceOrSet | None = None,
        require_tld: bool = True,
        error: str | None = None,
    ):
        """Constructor.

        :param relative: Whether to allow relative URLs.
        :param absolute: Whether to allow absolute URLs.
        :param error: Error message to raise in case of a validation error.
            Can be interpolated with `{input}`.
        :param schemes: Valid schemes. By default, ``http``, ``https``,
            ``ftp``, and ``ftps`` are allowed.
        :param require_tld: Whether to reject non-FQDN hostnames.
        """
        if not relative and not absolute:
            raise ValueError(
                "URL validation cannot set both relative and absolute to False."
            )
        self.relative = relative
        self.absolute = absolute
        self.error = error or self.default_message  # type: str
        self.schemes = schemes or self.default_schemes
        self.require_tld = require_tld

    def _repr_args(self) -> str:
        return f"relative={self.relative!r}, absolute={self.absolute!r}"

    def _format_error(self, value) -> str:
        return self.error.format(input=value)

    def __call__(self, value: str) -> str:
        """Run the validation.

        :param value: URL string to be validated.
        """
        message = self._format_error(value)
        if not value:
            raise ValidationError(message)

        # Check first if the scheme is valid
        if "://" in value:
            scheme = value.split("://")[0].lower()
            if scheme not in self.schemes:
                raise ValidationError(message)

        regex = self._regex(self.relative, self.absolute, self.require_tld)

        if not regex.search(value):
            raise ValidationError(message)

        return value


class URL(String):
    """URL field with custom URL validator.

    :param default: Default value for the field if the attribute is not set.
    :param relative: Whether to allow relative URLs.
    :param require_tld: Whether to reject non-FQDN hostnames.
    :param schemes: Valid schemes. By default, ``http``, ``https``,
        ``ftp``, and ``ftps`` are allowed.
    :param kwargs: The same keyword arguments that :class:`String` receives.
    """

    #: Default error messages.
    default_error_messages = {"invalid": "Not a valid URL."}

    def __init__(
        self,
        *,
        relative: bool = False,
        absolute: bool = True,
        schemes: types.StrSequenceOrSet | None = None,
        require_tld: bool = True,
        **kwargs,
    ):
        """Constructor.

        :param default: Default value for the field if the attribute is not set.
        :param relative: Whether to allow relative URLs.
        :param require_tld: Whether to reject non-FQDN hostnames.
        :param schemes: Valid schemes. By default, ``http``, ``https``,
            ``ftp``, and ``ftps`` are allowed.
        :param kwargs: The same keyword arguments that :class:`String` receives.
        """
        super().__init__(**kwargs)

        self.relative = relative
        self.absolute = absolute
        self.require_tld = require_tld
        # Insert validation into self.validators so that multiple errors can be stored.
        validator = URLValidator(
            relative=self.relative,
            absolute=self.absolute,
            schemes=schemes,
            require_tld=self.require_tld,
            error=self.error_messages["invalid"],
        )
        self.validators.insert(0, validator)
