# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

"""Tests for marshmallow GeoJSON Point schema."""

import pytest
from marshmallow import ValidationError

from marshmallow_utils.schemas import PointSchema


@pytest.mark.parametrize(
    "coordinates",
    [
        ([-32.94682, -60.63932]),
        ([-32.94682, -60.63932, 10.0]),
    ],
)
def test_point(coordinates):
    valid_full = {"type": "Point", "coordinates": coordinates}

    loaded = PointSchema().load(valid_full)
    # NOTE: Since the schemas return the dict itself, the loaded object
    # is the same than the input and dumped objects (dicts)
    assert valid_full == loaded == PointSchema().dump(loaded)


# NOTE: ["-32.94682", "-60.63932"] is valid because the Float field
# deserializes properly the string into float, so it becomes
# [-32.94682, -60.63932]
@pytest.mark.parametrize(
    "coordinates",
    [
        ("-32.94682,-60.63932"),
        (["-32.94682,-60.63932"]),
        ([-32.94682, -60.63932, 10.0, 10.0]),
        ([-32.94682]),
    ],
)
def test_point_fail(coordinates):
    invalid_point = {"type": "Point", "coordinates": coordinates}
    pytest.raises(ValidationError, PointSchema().load, invalid_point)
