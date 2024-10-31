""".. title:: Generate GeoJSON of 7 AM reports

Return to `API Services </api/#json>`_

Changelog
---------

- 2024-08-14: Documentation Update

Example Requests
----------------

Get reports for 7 AM on 1 July 2024

https://mesonet.agron.iastate.edu/geojson/7am.py?dt=2024-07-01

Get reports for 7 AM on 1 July 2024 for COOP stations

https://mesonet.agron.iastate.edu/geojson/7am.py?dt=2024-07-01&group=coop

Get the morning reports on that date for ASOS stations

https://mesonet.agron.iastate.edu/geojson/7am.py?dt=2024-07-01&group=azos

"""

import json
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.reference import ISO8601, TRACE_VALUE
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(
        default=None,
        description="Optional JSONP callback function name",
    )
    group: str = Field(
        default="coop",
        description="The group of stations to generate data for",
    )
    dt: date = Field(
        default=date.today(),
        description="Date to generate data for",
    )


def p(val, precision=2):
    """see if we can round values better?"""
    if val is None:
        return None
    if 0 < val < 0.001:
        return TRACE_VALUE
    return round(val, precision)


def router(group, ts):
    """Figure out which report to generate

    Args:
      group (str): the switch string indicating group
      ts (date): date we are interested in
    """
    if group == "coop":
        return run(
            ts,
            [
                "IA_COOP",
                "MO_COOP",
                "KS_COOP",
                "NE_COOP",
                "SD_COOP",
                "MN_COOP",
                "WI_COOP",
                "IL_COOP",
            ],
        )
    if group == "azos":
        return run_azos(ts)
    if group == "cocorahs":
        return run(ts, ["IACOCORAHS"])
    return None


def run_azos(ts):
    """Get the data please"""
    pgconn, cursor = get_dbconnc("iem")

    # Now we have the tricky work of finding what 7 AM is
    ts = ts.astimezone(ZoneInfo("America/Chicago"))
    ts1 = ts.replace(hour=7)
    ts0 = ts1 - timedelta(hours=24)
    cursor.execute(
        """
        select t.id, t.name, t.network, sum(phour), st_x(geom), st_y(geom)
        from hourly h JOIN stations t ON
        (h.iemid = t.iemid) where t.network in ('IA_ASOS', 'SD_ASOS',
        'NE_ASOS', 'KS_ASOS', 'MO_ASOS', 'IL_ASOS', 'WI_ASOS', 'MN_ASOS')
        and valid >= %s and valid < %s GROUP by t.id, t.network, t.name, t.geom
        """,
        (ts0, ts1),
    )

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utc().strftime(ISO8601),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                id=row["id"],
                properties=dict(
                    pday=p(row["sum"]),
                    snow=None,
                    snowd=None,
                    name=row["name"],
                    network=row["network"],
                ),
                geometry=dict(
                    type="Point", coordinates=[row["st_x"], row["st_y"]]
                ),
            )
        )
    pgconn.close()
    return json.dumps(res)


def run(ts, networks):
    """Actually do the hard work of getting the current SPS in geojson"""
    pgconn, cursor = get_dbconnc("iem")

    cursor.execute(
        """
        select id, ST_x(geom), ST_y(geom), coop_valid, pday, snow, snowd,
        extract(hour from coop_valid)::int as hour, max_tmpf as high,
        min_tmpf as low, coop_tmpf, name, network
        from summary s JOIN stations t ON (t.iemid = s.iemid)
        WHERE s.day = %s and t.network = ANY(%s) and pday >= 0
        and extract(hour from coop_valid) between 5 and 10
    """,
        (ts.date(), networks),
    )

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utc().strftime(ISO8601),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                id=row["id"],
                properties=dict(
                    pday=p(row["pday"]),
                    snow=p(row["snow"], 1),
                    snowd=p(row["snowd"], 1),
                    name=row["name"],
                    hour=row["hour"],
                    high=row["high"],
                    low=row["low"],
                    coop_tmpf=row["coop_tmpf"],
                    network=row["network"],
                ),
                geometry=dict(
                    type="Point", coordinates=[row["st_x"], row["st_y"]]
                ),
            )
        )
    pgconn.close()
    return json.dumps(res)


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey=lambda x: f"/geojson/7am/{x['dt']}/{x['group']}",
    memcacheexpire=15,
    content_type="application/vnd.geo+json",
)
def application(environ, start_response):
    """Do Workflow"""
    group = environ["group"]
    dt = environ["dt"]
    ts = utc(dt.year, dt.month, dt.day, 12)

    res = router(group, ts)
    headers = [("Content-type", "application/vnd.geo+json")]
    start_response("200 OK", headers)
    return res
