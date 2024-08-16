"""Test iemweb.request.coop module."""

from datetime import date

import pytest
from iemweb.request.coop import (
    do_apsim,
    do_century,
    do_daycent,
    do_dndc,
    do_salus,
    do_simple,
    do_swat,
)


@pytest.mark.parametrize("database", ["coop"])
def test_simple(dbcursor):
    """Test the requests."""
    ctx = {
        "what": "simple",
        "stations": ["IATDSM"],
        "scenario_sts": date(2023, 12, 2),
        "scenario_ets": date(2023, 12, 31),
        "scenario_year": 2023,
        "sts": date(2020, 1, 1),
        "ets": date(2020, 12, 1),  # Note we wish to fill out the year
        "inclatlon": True,
        "gis": True,
        "myvars": [],
        "with_header": True,
        "scenario": True,
        "delim": "comma",
    }
    res = do_simple(dbcursor, ctx)
    assert len(res.decode("ascii").strip().split("\n")) == (366 + 6)
    for f in [
        do_apsim,
        do_century,
        do_daycent,
        do_dndc,
        do_salus,
        do_swat,
    ]:
        res = f(dbcursor, ctx)
        assert res is not None
