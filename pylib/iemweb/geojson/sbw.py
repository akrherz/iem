""".. title:: Service for Storm Based Warnings GeoJSON

Return to `API Services </api/#json>`_

Documentation for /geojson/sbw.geojson
--------------------------------------

This service supports a number of legacy systems and implements a number of
different calling methods.  The `API <https://mesonet.agron.iastate.edu
/api/1/docs#/vtec/service_vtec_sbw_interval__fmt__get>`_ service is recommended
for new applications.

Changelog
---------

- 2024-12-31: Five additional metadata fields are added with lifetime max
  values for windtag, hailtag, is_pds, is_emergency, and floodtag_damage. These
  fields are prefixed with `max_`.
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
from typing import Optional

from pydantic import AwareDatetime, Field, field_validator, model_validator
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

    @model_validator(mode="after")
    def ensure_some_timestamp(self):
        """Ensure that we have some timestamp set."""
        if self.ts is None and self.sts is None and self.ets is None:
            self.ts = utc()
        if (self.sts is not None and self.ets is None) or (
            self.sts is None and self.ets is not None
        ):
            raise ValueError("Both sts and ets must be provided")
        return self


def df(val: Optional[datetime]):
    """Format a datetime object"""
    return None if val is None else val.strftime(ISO8601)


def run(environ: dict):
    """Actually do the hard work of getting the current SBW in geojson"""
    wfos = environ["wfos"]
    if wfos is not None and wfos[0] == "":
        wfos = None
    if wfos is None and environ["wfo"] is not None:
        wfos = [environ["wfo"]]

    params = {
        "wfos": wfos,
        "ts": environ["ts"],
        "sts": environ["sts"],
        "ets": environ["ets"],
    }

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utc().strftime(ISO8601),
    }

    wfo_limiter = ""
    if wfos:
        wfo_limiter = " and s.wfo = ANY(:wfos) "
    time_limiter = " s.expire > :sts and s.issue < :ets "
    status_limiter = " and s.status = 'NEW' "
    # Mode 2, ts is provided, so we get polygons valid at this time
    if environ["ts"] is not None:
        time_limiter = (
            " s.polygon_begin <= :ts and s.polygon_end > :ts and "
            " s.polygon_begin > :pastts "
        )
        status_limiter = ""
        params["pastts"] = environ["ts"] - timedelta(days=14)  # arb
        res["valid_at"] = environ["ts"].strftime(ISO8601)

    # NOTE: we dropped checking for products valid in the future (FL.W)
    # NOTE: we have an arb offset check for child table exclusion
    with get_sqlalchemy_conn("postgis") as conn:
        rs = conn.execute(
            text(f"""
    with tagmaxes as (
        select wfo, phenomena, vtec_year, eventid, significance,
        max(windtag) as max_windtag,
        max(hailtag) as max_hailtag,
        bool_or(is_pds) as max_is_pds,
        bool_or(is_emergency) as max_is_emergency,
        bool_or(floodtag_damage = 'CATASTROPHIC')
                as floodtag_damage_catastrophic,
        bool_or(floodtag_damage = 'CONSIDERABLE')
                as floodtag_damage_considerable
        from sbw s WHERE s.expire > :sts and s.issue < :ets {wfo_limiter}
        GROUP by wfo, phenomena, vtec_year, eventid, significance
    )
            SELECT ST_asGeoJson(geom) as geojson, s.phenomena, s.eventid,
            s.wfo, s.significance,
            s.polygon_end at time zone 'UTC' as utc_polygon_end,
            s.polygon_begin at time zone 'UTC' as utc_polygon_begin,
            s.status,
            s.hvtec_nwsli, s.vtec_year, s.product_id,
            s.issue at time zone 'UTC' as utc_issue,
            s.expire at time zone 'UTC' as utc_expire, s.windtag, s.hailtag,
            s.tornadotag, s.damagetag, s.waterspouttag, s.is_emergency,
            s.is_pds, s.windthreat, s.hailthreat, s.product_signature,
            s.floodtag_damage, s.squalltag,
            t.max_windtag, t.max_hailtag, t.max_is_pds, t.max_is_emergency,
            case when t.floodtag_damage_catastrophic then 'CATASTROPHIC'
                    when t.floodtag_damage_considerable then 'CONSIDERABLE'
                    else null end as max_floodtag_damage
            from sbw s, tagmaxes t WHERE s.vtec_year = t.vtec_year and
            s.wfo = t.wfo and s.phenomena = t.phenomena and
            s.significance = t.significance and s.eventid = t.eventid and
            {time_limiter} {status_limiter} {wfo_limiter}
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
                        floodtag_damage=row["floodtag_damage"],
                        squalltag=row["squalltag"],
                        max_windtag=row["max_windtag"],
                        max_hailtag=row["max_hailtag"],
                        max_is_pds=row["max_is_pds"],
                        max_is_emergency=row["max_is_emergency"],
                        max_floodtag_damage=row["max_floodtag_damage"],
                    ),
                    geometry=json.loads(row["geojson"]),
                )
            )
    res["count"] = len(res["features"])
    return json.dumps(res)


def get_mcexpire(environ: dict) -> int:
    """Compute the cache expiration time."""
    return 15 if environ["ts"] is None else 600


def get_mckey(environ):
    """Compute the key."""
    wfos = environ["wfos"]
    if wfos is None and environ["wfo"] is not None:
        wfos = [environ["wfo"]]
    if wfos is None:
        wfos = []
    ts = environ["ts"]
    if environ["sts"] is not None:
        ts = f"{environ['sts']:%Y%m%d%H%M}_to_{environ['ets']:%Y%m%d%H%M}"
    else:
        ts = ts.strftime(ISO8601)

    return f"/geojson/sbw.geojson|{ts}|{','.join(wfos)[:100]}"


@iemapp(
    help=__doc__,
    schema=Schema,
    content_type="application/vnd.geo+json",
    memcachekey=get_mckey,
    memcacheexpire=get_mcexpire,
    parse_times=False,
)
def application(environ, start_response):
    """Main Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]
    res = run(environ)
    start_response("200 OK", headers)
    return res.encode("utf-8")
