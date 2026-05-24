# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

"""Module tests."""


def test_version():
    """Test version import."""
    from marshmallow_utils import __version__

    assert __version__
