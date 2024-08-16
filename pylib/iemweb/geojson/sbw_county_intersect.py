""".. title:: Storm Based Warning County Intersection

Return to `API Services </api/#json>`_. This service drives some of the
presentation of the `VTEC Browser </vtec/>`_.

This service provides a GeoJSON for the intersection of the polygon border and
any county/parish borders.  This is meant to describe the amount of the polygon
border that was influenced by the county border.

Changelog
---------

- 2024-08-16: Initial documentation update

Example Usage
-------------

Show the intersection of the polygon border for Des Moines Tornado Warning 49
from 2024 with county borders.

https://mesonet.agron.iastate.edu/geojson/sbw_county_intersect.py\
?wfo=KDMX&year=2024&phenomena=TO&significance=W&eventid=49

"""

import geopandas as gpd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    wfo: str = Field("MPX", description="3 or 4 character WFO Identifier")
    year: int = Field(2015, description="Year of interest")
    phenomena: str = Field("SV", description="VTEC Phenomena", max_length=2)
    significance: str = Field(
        "W", description="VTEC Significance", max_length=1
    )
    eventid: int = Field(1, description="VTEC Event ID", ge=1, le=9999)


def run(wfo, year, phenomena, significance, eventid):
    """Do great things"""
    with get_sqlalchemy_conn("postgis") as conn:
        borderdf = gpd.read_postgis(
            text("""
            WITH stormbased as (
                SELECT geom from sbw where vtec_year = :year and wfo = :wfo
                and eventid = :eventid and significance = :significance
                and phenomena = :phenomena and status = 'NEW' limit 1),
            countybased as (
                SELECT ST_Union(u.geom) as geom from
                warnings w JOIN ugcs u on (u.gid = w.gid)
                WHERE w.vtec_year = :year and w.wfo = :wfo and
                eventid = :eventid and significance = :significance
                and phenomena = :phenomena),
            foo as (
                 SELECT ST_SetSRID(ST_intersection(
          ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(c.geom),1)),0.02),
          ST_exteriorring(ST_geometryn(ST_multi(s.geom),1))
            ), 4326) as geom from stormbased s, countybased c)

            SELECT geom, ST_Length(ST_transform(geom,9311)) as sz from foo
        """),
            conn,
            params=dict(
                year=year,
                wfo=wfo,
                phenomena=phenomena,
                significance=significance,
                eventid=eventid,
            ),
            geom_col="geom",
        )
    return borderdf.to_json()


def get_mckey(environ: dict) -> str:
    """Return the key."""
    return (
        f"/geojson/sbw_county_intersect/{environ['wfo']}/{environ['year']}/"
        f"{environ['phenomena']}/{environ['significance']}/"
        f"{environ['eventid']}"
    )


@iemapp(
    schema=Schema,
    help=__doc__,
    content_type="application/vnd.geo+json",
    memcacheexpire=3600,
    memcachekey=get_mckey,
)
def application(environ, start_response):
    """Main()"""
    headers = [("Content-type", "application/vnd.geo+json")]

    wfo = environ["wfo"]
    if len(wfo) == 4:
        wfo = wfo[1:]

    res = run(
        wfo,
        environ["year"],
        environ["phenomena"],
        environ["significance"],
        environ["eventid"],
    )

    start_response("200 OK", headers)
    return res.encode("ascii")
