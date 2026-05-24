# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

"""Marshmallow schemas."""

from .geojson import GeometryObjectSchema, MultiPointSchema, PointSchema, PolygonSchema
from .identifier import IdentifierSchema

__all__ = (
    "GeometryObjectSchema",
    "IdentifierSchema",
    "MultiPointSchema",
    "PointSchema",
    "PolygonSchema",
)
