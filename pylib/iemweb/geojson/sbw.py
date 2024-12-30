""".. title:: Service for Storm Based Warnings GeoJSON

Return to `API Services </api/#json>`_

Documentation for /geojson/sbw.geojson
--------------------------------------

This service supports a number of legacy systems and implements a number of
different calling methods.  The usage of `sts` and `ets` is discouraged and
you should instead use the `API <https://mesonet.agron.iastate.edu
/api/1/docs#/vtec/service_vtec_sbw_interval__fmt__get>`_.

Changelog
---------

- 2024-12-30: Parameters `sts` and `ets` can now be provided as ISO8601
  formatted strings.  The legacy format of %Y%m%d%H%M is still supported, but
  discouraged.
- 2024-11-19: Trimmed caching time from 60s to 15s. Added `ps` attribute that
  holds the VTEC Phenomena and Significance string.
- 2024-11-04: A number of additional metadata fields were added to the output
- 2024-07-01: Initial documentation release

Examples
--------

Provide all SBW polygons active at a given timestamp:

https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts=2024-05-26T20:00:00Z

Provide all SBW polygons on 26 May 2024 CDT.

https://mesonet.agron.iastate.edu/geojson/sbw.geojson\
?sts=2024-05-26T05:00:00Z&ets=2024-05-27T05:00:00Z

"""

import json
from datetime import datetime, timedelta, timezone

from pydantic import AwareDatetime, Field, field_validator
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.vtec import get_ps_string
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

from iemweb.imagemaps import rectify_wfo


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(
        default=None,
        description="Optional JSONP callback function name",
    )
    ets: AwareDatetime = Field(
        default=None,
        description=(
            "Legacy UTC end timestamp parameter in the form of YYYYmmddHHMM"
        ),
    )
    sts: AwareDatetime = Field(
        default=None,
        description=(
            "Legacy UTC start timestamp parameter in the form of YYYYmmddHHMM"
        ),
    )
    ts: AwareDatetime = Field(
        default=None,
        description=(
            "If sts and ets are not provided, this is the timestamp to "
            "request data for."
        ),
    )
    wfo: str = Field(
        default=None,
        description="Optional WFO identifier",
        max_length=3,
        min_length=3,
    )
    wfos: ListOrCSVType = Field(
        default=None,
        description="Optional list of WFOs to limit the results to",
    )

    @field_validator("sts", "ets", mode="before")
    def legacy_timestamps(cls, value, _info):
        """Allow the junky old way to work."""
        fmt = "%Y%m%d%H%M"
        if value.find("T") > 0 and len(value) >= 16:
            fmt = "%Y-%m-%dT%H:%M"
            value = value[:16]
        return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)


def df(val):
    """Format a datetime object"""
    if val is None:
        return None
    return val.strftime(ISO8601)


def run(environ: dict):
    """Actually do the hard work of getting the current SBW in geojson"""
    wfos = environ["wfos"]
    if wfos is not None and wfos[0] == "":
        wfos = None
    if wfos is None and environ["wfo"] is not None:
        wfos = [environ["wfo"]]
    if (
        environ["ts"] is None
        and environ["sts"] is None
        and environ["ets"] is None
    ):
        environ["ts"] = utc()

    params = {
        "wfos": wfos,
        "ts": environ["ts"],
        "sts": environ["sts"],
        "ets": environ["ets"],
    }

    wfo_limiter = ""
    if wfos:
        wfo_limiter = " and wfo = ANY(:wfos) "
    time_limiter = " expire > :sts and issue < :ets and status = 'NEW' "
    # Mode 2, ts is provided, so we get polygons valid at this time
    if environ["ts"] is not None:
        time_limiter = (
            " polygon_begin <= :ts and polygon_end > :ts and "
            " polygon_begin > :pastts "
        )
        params["pastts"] = environ["ts"] - timedelta(days=14)  # arb

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utc().strftime(ISO8601),
    }
    if environ["ts"] is not None:
        res["valid_at"] = environ["ts"].strftime(ISO8601)

    # NOTE: we dropped checking for products valid in the future (FL.W)
    # NOTE: we have an arb offset check for child table exclusion
    with get_sqlalchemy_conn("postgis") as conn:
        rs = conn.execute(
            text(f"""
            SELECT ST_asGeoJson(geom) as geojson, phenomena, eventid, wfo,
            significance, polygon_end at time zone 'UTC' as utc_polygon_end,
            polygon_begin at time zone 'UTC' as utc_polygon_begin, status,
            hvtec_nwsli, vtec_year, product_id,
            issue at time zone 'UTC' as utc_issue,
            expire at time zone 'UTC' as utc_expire, windtag, hailtag,
            tornadotag, damagetag, waterspouttag, is_emergency, is_pds,
            windthreat, hailthreat, product_signature
            from sbw WHERE {time_limiter} {wfo_limiter}
        """),
            params,
        )
        for row in rs.mappings():
            sid = (
                f"{row['wfo']}.{row['phenomena']}.{row['significance']}."
                f"{row['eventid']:04.0f}"
            )
            ets = row["utc_polygon_end"].strftime(ISO8601)
            sts = row["utc_polygon_begin"].strftime(ISO8601)
            sid += "." + sts
            href = (
                "https://mesonet.agron.iastate.edu/vtec/event/"
                f"{row['vtec_year']}-0-{row['status']}-"
                f"{rectify_wfo(row['wfo'])}-{row['phenomena']}-"
                f"{row['significance']}-{row['eventid']:04.0f}"
            )
            label = get_ps_string(row["phenomena"], row["significance"])
            link = f"<a href='{href}'>{label} {row['eventid']}</a> &nbsp; "
            res["features"].append(
                dict(
                    type="Feature",
                    id=sid,
                    properties=dict(
                        status=row["status"],
                        phenomena=row["phenomena"],
                        significance=row["significance"],
                        ps=label,
                        wfo=row["wfo"],
                        eventid=row["eventid"],
                        polygon_begin=sts,
                        polygon_end=ets,
                        expire=df(row["utc_expire"]),
                        hvtec_nwsli=row["hvtec_nwsli"],
                        year=row["vtec_year"],
                        product_id=row["product_id"],
                        issue=df(row["utc_issue"]),
                        expire_utc=df(row["utc_expire"]),
                        href=href,
                        link=link,
                        windtag=row["windtag"],
                        hailtag=row["hailtag"],
                        tornadotag=row["tornadotag"],
                        damagetag=row["damagetag"],
                        waterspouttag=row["waterspouttag"],
                        is_emergency=row["is_emergency"],
                        is_pds=row["is_pds"],
                        windthreat=row["windthreat"],
                        hailthreat=row["hailthreat"],
                        product_signature=row["product_signature"],
                    ),
                    geometry=json.loads(row["geojson"]),
                )
            )
    res["count"] = len(res["features"])
    return json.dumps(res)


def get_mckey(environ):
    """Compute the key."""
    wfos = environ["wfos"]
    if wfos is None and environ["wfo"] is not None:
        wfos = [environ["wfo"]]
    if wfos is None:
        wfos = []
    ts = environ["ts"]
    if ts is None:
        ts = f"{environ['sts']:%Y%m%d%H%M}_to_{environ['ets']:%Y%m%d%H%M}"
    else:
        ts = ts.strftime(ISO8601)

    return f"/geojson/sbw.geojson|{ts}|{','.join(wfos)[:100]}"


@iemapp(
    help=__doc__,
    schema=Schema,
    content_type="application/vnd.geo+json",
    memcachekey=get_mckey,
    memcacheexpire=15,
    parse_times=False,
)
def application(environ, start_response):
    """Main Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]
    res = run(environ)
    start_response("200 OK", headers)
    return res.encode("utf-8")
