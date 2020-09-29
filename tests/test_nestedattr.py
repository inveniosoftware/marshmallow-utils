from datetime import date
from pprint import pprint

from marshmallow import Schema, fields

from marshmallow_utils.fields import nestedattr


class MyArtist(dict):
    """Artist class."""

    @property
    def name(self):
        """Name."""
        return 'property'


class ArtistSchema(Schema):
    """Artist Schema."""

    name = fields.Str()


class AlbumSchema(Schema):
    """Album Schema."""

    '''
    artist = fields.Nested(ArtistSchema())
    '''
    artist = nestedattr.NestedAttribute(ArtistSchema())


def test_test_schema():
    bowie = MyArtist(name="david")
    album = dict(artist=bowie,
                 title="Hunky Dory",
                 release_date=date(1971, 12, 17))

    schema = AlbumSchema()
    result = schema.dump(album)

    assert result['artist'] == {'name': 'property'}
