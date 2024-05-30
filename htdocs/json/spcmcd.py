"""SPC MCD service."""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP Callback Name")
    lat: float = Field(
        42.0, description="Latitude of point in decimal degrees"
    )
    lon: float = Field(
        -95.0, description="Longitude of point in decimal degrees"
    )


def dowork(lon, lat):
    """Actually do stuff"""
    data = {"generated_at": utc().strftime(ISO8601), "mcds": []}
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text("""
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e, watch_confidence,
        num, product_id, year, concerning from mcd WHERE
        ST_Contains(geom, ST_Point(:lon, :lat, 4326))
        ORDER by product_id DESC
    """),
            {"lon": lon, "lat": lat},
        )
        for row in res:
            row = row._asdict()
            url = (
                "https://www.spc.noaa.gov/products/md/"
                f"{row['year']}/md{row['num']:04.0f}.html"
            )
            data["mcds"].append(
                dict(
                    spcurl=url,
                    year=row["year"],
                    utc_issue=row["i"].strftime(ISO8601),
                    utc_expire=row["e"].strftime(ISO8601),
                    product_num=row["num"],
                    product_id=row["product_id"],
                    product_href=(
                        "https://mesonet.agron.iastate.edu/"
                        f"p.php?pid={row['product_id']}"
                    ),
                    concerning=row["concerning"],
                    watch_confidence=row["watch_confidence"],
                )
            )
    return json.dumps(data)


def get_mckey(environ):
    """Get memcache key."""
    return f"/json/spcmcd/{environ['lon']:.4f}/{environ['lat']:.4f}"


@iemapp(help=__doc__, schema=Schema, memcachekey=get_mckey)
def application(environ, start_response):
    """Answer request."""
    lat = environ["lat"]
    lon = environ["lon"]

    res = dowork(lon, lat)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
