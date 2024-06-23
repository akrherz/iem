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
        "scenario_sts": date(2020, 1, 1),
        "scenario_ets": date(2020, 12, 31),
        "scenario_year": 2023,
        "sts": date(2020, 1, 1),
        "ets": date(2020, 12, 31),
        "inclatlon": True,
        "gis": True,
        "myvars": [],
        "with_header": True,
        "scenario": True,
        "delim": "comma",
    }
    for f in [
        do_apsim,
        do_century,
        do_daycent,
        do_dndc,
        do_salus,
        do_simple,
        do_swat,
    ]:
        res = f(dbcursor, ctx)
        assert res is not None
