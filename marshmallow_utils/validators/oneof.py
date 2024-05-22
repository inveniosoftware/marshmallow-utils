# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2024 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Lazy OneOf validator."""

import typing

from marshmallow import validate


class LazyOneOf(validate.OneOf):
    """Lazy version of the default marshmallow OneOf validator."""

    def __init__(
        self,
        choices: typing.Union[typing.Iterable, typing.Callable[[], typing.Iterable]],
        labels: typing.Union[
            typing.Iterable[str], typing.Callable[[], typing.Iterable], None
        ] = None,
        *,
        error: typing.Union[str, None] = None,
    ):
        """Initialize validator."""
        self._choices = choices
        self._labels = labels if labels is not None else []
        self.error = error or self.default_message  # type: str

    @property
    def choices(self) -> typing.Iterable:
        """Return the choices."""
        if callable(self._choices):
            return self._choices()
        return self._choices

    @property
    def choices_text(self) -> str:
        """Return the choices as a string."""
        return ", ".join(str(choice) for choice in self.choices)

    @property
    def labels(self) -> typing.Iterable[str]:
        """Return the labels."""
        if callable(self._labels):
            return self._labels()
        return self._labels

    @property
    def labels_text(self) -> str:
        """Return the labels as a string."""
        return ", ".join(str(label) for label in self.labels)
