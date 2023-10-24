# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2023 CERN.
# Copyright 2021 Steven Loria and contributors
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for fields.url"""

import re

import pytest
from marshmallow import ValidationError, validate

from marshmallow_utils.fields.url import URLValidator


@pytest.mark.parametrize(
    "valid_url",
    [
        "http://example.org",
        "https://example.org",
        "ftp://example.org",
        "ftps://example.org",
        "http://example.co.jp",
        "http://www.example.com/a%C2%B1b",
        "http://www.example.com/~username/",
        "http://info.example.com/?fred",
        "http://xn--mgbh0fb.xn--kgbechtv/",
        "http://example.com/blue/red%3Fand+green",
        "http://www.example.com/?array%5Bkey%5D=value",
        "http://xn--rsum-bpad.example.org/",
        "http://123.45.67.8/",
        "http://123.45.67.8:8329/",
        "http://[2001:db8::ff00:42]:8329",
        "http://[2001::1]:8329",
        "http://www.example.com:8000/foo",
        "http://user@example.com",
        "http://user:pass@example.com",
        "http://xn__mgbh0fb.xn--kgbechtv/",
        "http://xn__mg--bh__0fb.xn--kgbechtv/",
    ],
)
def test_url_absolute_valid(valid_url):
    validator = URLValidator(relative=False)
    assert validator(valid_url) == valid_url


@pytest.mark.parametrize(
    "invalid_url",
    [
        "http:///example.com/",
        "https:///example.com/",
        "https://example.org\\",
        "https://example.org\n",
        "ftp:///example.com/",
        "ftps:///example.com/",
        "http//example.org",
        "http:///",
        "http:/example.org",
        "foo://example.org",
        "../icons/logo.gif",
        "http://2001:db8::ff00:42:8329",
        "http://[192.168.1.1]:8329",
        "http://xn_-mgbh0fb.xn--kgbechtv/",
        "http://xn-_mg--bh__0fb.xn--kgbechtv/",
        "http://-example.co.jp",
        "http://_example.co.jp",
        "http://example-.co.jp",
        "http://example_.co.jp",
        "abc",
        "..",
        "/",
        " ",
        "",
        None,
    ],
)
def test_url_absolute_invalid(invalid_url):
    validator = URLValidator(relative=False)
    with pytest.raises(ValidationError):
        validator(invalid_url)


@pytest.mark.parametrize(
    "valid_url",
    [
        "http://example.org",
        "http://123.45.67.8/",
        "http://example.com/foo/bar/../baz",
        "https://example.com/../icons/logo.gif",
        "http://example.com/./icons/logo.gif",
        "ftp://example.com/../../../../g",
        "http://example.com/g?y/./x",
        "/foo/bar",
        "/foo?bar",
        "/foo?bar#baz",
    ],
)
def test_url_relative_valid(valid_url):
    validator = URLValidator(relative=True)
    assert validator(valid_url) == valid_url


@pytest.mark.parametrize(  # noqa: W605
    "invalid_url",
    [
        "http//example.org",
        "http://example.org\n",
        "suppliers.html",
        "../icons/logo.gif",
        "icons/logo.gif",
        "../.../g",
        "...",
        "\\",
        " ",
        "",
        None,
    ],
)
def test_url_relative_invalid(invalid_url):
    validator = URLValidator(relative=True)
    with pytest.raises(ValidationError):
        validator(invalid_url)


@pytest.mark.parametrize(
    "valid_url",
    [
        "/foo/bar",
        "/foo?bar",
        "?bar",
        "/foo?bar#baz",
    ],
)
def test_url_relative_only_valid(valid_url):
    validator = URLValidator(relative=True, absolute=False)
    assert validator(valid_url) == valid_url


@pytest.mark.parametrize(
    "invalid_url",
    [
        "http//example.org",
        "http://example.org\n",
        "suppliers.html",
        "../icons/logo.gif",
        "icons/logo.gif",
        "../.../g",
        "...",
        "\\",
        " ",
        "",
        "http://example.org",
        "http://123.45.67.8/",
        "http://example.com/foo/bar/../baz",
        "https://example.com/../icons/logo.gif",
        "http://example.com/./icons/logo.gif",
        "ftp://example.com/../../../../g",
        "http://example.com/g?y/./x",
    ],
)
def test_url_relative_only_invalid(invalid_url):
    validator = URLValidator(relative=True, absolute=False)
    with pytest.raises(ValidationError):
        validator(invalid_url)


@pytest.mark.parametrize(
    "valid_url",
    [
        "http://example.org",
        "http://123.45.67.8/",
        "http://example",
        "http://example.",
        "http://example:80",
        "http://user.name:pass.word@example",
        "http://example/foo/bar",
    ],
)
def test_url_dont_require_tld_valid(valid_url):
    validator = URLValidator(require_tld=False)
    assert validator(valid_url) == valid_url


@pytest.mark.parametrize(
    "invalid_url",
    [
        "http//example",
        "http://example\n",
        "http://.example.org",
        "http:///foo/bar",
        "http:// /foo/bar",
        "",
        None,
    ],
)
def test_url_dont_require_tld_invalid(invalid_url):
    validator = URLValidator(require_tld=False)
    with pytest.raises(ValidationError):
        validator(invalid_url)


def test_url_custom_scheme():
    validator = URLValidator()
    # By default, ws not allowed
    url = "ws://test.test"
    with pytest.raises(ValidationError):
        validator(url)

    validator = URLValidator(schemes={"http", "https", "ws"})
    assert validator(url) == url


def test_url_relative_and_custom_schemes():
    validator = URLValidator(relative=True)
    # By default, ws not allowed
    url = "ws://test.test"
    with pytest.raises(ValidationError):
        validator(url)

    validator = URLValidator(relative=True, schemes={"http", "https", "ws"})
    assert validator(url) == url


def test_url_custom_message():
    validator = URLValidator(error="{input} ain't an URL")
    with pytest.raises(ValidationError, match="invalid ain't an URL"):
        validator("invalid")


def test_url_repr():
    assert repr(
        URLValidator(relative=False, error=None)
    ) == "<URLValidator(relative=False, absolute=True, error={!r})>".format(
        "Not a valid URL."
    )
    assert repr(
        URLValidator(relative=True, error="foo")
    ) == "<URLValidator(relative=True, absolute=True, error={!r})>".format("foo")
    assert repr(
        URLValidator(relative=True, absolute=False, error="foo")
    ) == "<URLValidator(relative=True, absolute=False, error={!r})>".format("foo")


def test_url_rejects_invalid_relative_usage():
    with pytest.raises(
        ValueError,
        match="URL validation cannot set both relative and absolute to False",
    ):
        URLValidator(relative=False, absolute=False)
