"""Test some field heuristics."""

import pytest
from iemweb.fields import (
    STATION_LIST_FIELD,
    TZ_FIELD,
)
from pydantic import BaseModel, ValidationError


@pytest.fixture
def station_model():
    """Return a basemodel for testing."""

    class Model(BaseModel):
        station: STATION_LIST_FIELD
        tz: TZ_FIELD = "UTC"

    return Model


def test_tz_aliases(station_model):
    """Test that these are handled."""
    assert station_model(station="A", tz="").tz == "UTC"
    assert station_model(station="A", tz="etc/utc").tz == "UTC"


def test_bad_tz(station_model):
    """Test that this fails validation."""
    with pytest.raises(ValidationError, match="Unknown timezone: BAD!TZ"):
        station_model(station="A", tz="BAD!TZ")


def test_no_station(station_model):
    """Test what happens when no station is provided"""
    with pytest.raises(ValidationError, match="Field required"):
        station_model()


def test_station_list_field(station_model):
    """Test the station list field."""
    assert station_model(station="DSM").station == ["DSM"]
    assert station_model(station="DSM, OMA").station == ["DSM", "OMA"]
    assert station_model(station=" DSM , oMA ").station == ["DSM", "OMA"]
    assert station_model(station=["DSM ", "OMA"]).station == ["DSM", "OMA"]


def test_naughty_station_list_field(station_model):
    """That that these fail validation"""
    with pytest.raises(ValueError, match="Invalid station"):
        station_model(station="DSM, OMA, BAD!STN")
    with pytest.raises(ValueError, match="Invalid station"):
        station_model(station="BAD!STN")
