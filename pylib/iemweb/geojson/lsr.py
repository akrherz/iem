""".. title:: Local Storm Reports GeoJSON and More

Return to `API Services </api/#json>`_

This service does a number of different things with Local Storm Reports.

Changelog
---------

- 2024-07-14: This service was migrated from a PHP based script to python. An
  attempt was made to not break the attribute names and types.

Example Requests
----------------

Provide all Local Storm Reports for Wisconsin on 13 July 2024. Note that a
UTC date period is specified that equates to the US Central date.

https://mesonet.agron.iastate.edu/geojson/lsr.geojson?states=WI&\
sts=2024-07-13T05:00Z&ets=2024-07-14T05:00Z

Provide the LSRs associated with Des Moines Tornado Warning 47

https://mesonet.agron.iastate.edu/geojson/lsr.geojson?phenomena=TO&\
significance=W&eventid=47&year=2024&wfo=DMX

"""

from datetime import datetime, timezone

import geopandas as gpd
from pydantic import Field, field_validator
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.vtec import get_ps_string
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function")
    inc_ap: bool = Field(
        default=False,
        description="Include any associated warnings in the output.",
    )
    eventid: int = Field(
        default=103,
        description="If provided, use the given eventid to find LSRs for.",
    )
    phenomena: str = Field(
        default=None,
        description="If provided, use the given VTEC event to find LSRs for.",
        max_length=2,
    )
    significance: str = Field(
        default="W",
        description="If provided, use the given VTEC event to find LSRs for.",
        max_length=1,
    )
    states: ListOrCSVType = Field(
        default=[],
        description="If provided, use the given states to find LSRs for.",
    )
    ets: datetime = Field(
        default=None,
        description="Legacy and poorly constructed parameter YYYYmmddHHMI.",
    )
    sts: datetime = Field(
        default=None,
        description="Legacy and poorly constructed parameter YYYYmmddHHMI.",
    )
    wfo: str = Field(
        default=None,
        description="If provided, use the given WFO to find LSRs for.",
        max_length=4,
    )
    wfos: ListOrCSVType = Field(
        default=[],
        description="If provided, use the given WFOs to find LSRs for.",
    )
    year: int = Field(
        default=2006,
        description="If provided, use this year for the given VTEC event.",
    )

    @field_validator("ets", "sts", mode="before")
    @classmethod
    def parse_valid(cls, value, _info):
        """Ensure we have a valid time."""
        if value is None:
            return None
        fmt = "%Y%m%d%H%M"
        if value.find("T") > 0 and len(value) >= 16:
            fmt = "%Y-%m-%dT%H:%M"
            value = value[:16]
        return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)


def do_vtec(environ: dict) -> gpd.GeoDataFrame:
    """Actually do the hard work of getting the current SBW in geojson"""
    with get_sqlalchemy_conn("postgis") as conn:
        lsrdf = gpd.read_postgis(
            text(
                """
            SELECT l.wfo, l.type,
            l.magnitude as magf, l,county, l.typetext,
            l.state, l.remark, l.city, l.source, l.unit, l.geom,
            to_char(valid at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ')
                as valid,
            ST_x(l.geom) as lon, ST_y(l.geom) as lat
            from sbw w, lsrs l
            WHERE w.vtec_year = :year and w.wfo = :wfo and
            w.phenomena = :phenomena and
            w.eventid = :eventid and w.significance = :significance
            and w.geom && l.geom and l.valid BETWEEN w.issue and w.expire
            and w.status = 'NEW'
                """
            ),
            conn,
            params={
                "year": environ["year"],
                "wfo": environ["wfo"],
                "phenomena": environ["phenomena"],
                "eventid": environ["eventid"],
                "significance": environ["significance"],
            },
            geom_col="geom",
        )
    return lsrdf


def do_states(environ: dict) -> gpd.GeoDataFrame:
    """Actually do the hard work of getting the current SBW in geojson"""
    with get_sqlalchemy_conn("postgis") as conn:
        lsrdf = gpd.read_postgis(
            text(
                """
            SELECT distinct l.wfo, l.type,
            l.magnitude as magf, l,county, l.typetext,
            l.state, l.remark, l.city, l.source, l.unit, l.geom,
            to_char(valid at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ')
                as valid,
            ST_x(l.geom) as lon, ST_y(l.geom) as lat
            FROM lsrs l, states s WHERE
            valid BETWEEN :sts and :ets and state_abbr = ANY(:states)
            and ST_Intersects(l.geom, s.the_geom)
            LIMIT 10000
                """
            ),
            conn,
            params={
                "states": environ["states"],
                "ets": environ["ets"],
                "sts": environ["sts"],
            },
            geom_col="geom",
        )
    return lsrdf


def do_default(environ: dict) -> gpd.GeoDataFrame:
    """Actually do the hard work of getting the current SBW in geojson"""
    wfo_limiter = ""
    if environ["wfos"]:
        wfo_limiter = " and wfo = ANY(:wfos) "
    with get_sqlalchemy_conn("postgis") as conn:
        lsrdf = gpd.read_postgis(
            text(
                f"""
            SELECT distinct wfo, type, magnitude as magf,
            county, typetext, state, remark, city, source, unit,
            to_char(valid at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ')
                as valid,
            ST_x(geom) as lon, ST_y(geom) as lat, geom
            FROM lsrs WHERE
            valid BETWEEN :sts and :ets {wfo_limiter}
            LIMIT 10000
                """
            ),
            conn,
            params={
                "wfos": environ["wfos"],
                "ets": environ["ets"],
                "sts": environ["sts"],
            },
            geom_col="geom",
        )
    return lsrdf


def add_warnings(lsrdf: gpd.GeoDataFrame) -> None:
    """Add any associated warnings to the LSRs."""
    lsrdf["prodlinks"] = ""
    with get_sqlalchemy_conn("postgis") as conn:
        for idx, row in lsrdf.iterrows():
            res = conn.execute(
                text("""
                SELECT distinct phenomena, significance, eventid, vtec_year
                from sbw
                WHERE vtec_year = :year and wfo = :wfo and issue <= :valid
                and issue > :valid  - '7 days'::interval and expire > :valid
                and ST_POINT(:lon, :lat, 4326) && geom
                and ST_contains(geom, ST_POINT(:lon, :lat, 4326))
                """),
                {
                    "year": row["valid"][:4],
                    "wfo": row["wfo"],
                    "valid": row["valid"],
                    "lon": row["lon"],
                    "lat": row["lat"],
                },
            )
            products = ""
            for row2 in res.mappings():
                url = (
                    f"/vtec/#{row2['vtec_year']}-O-NEW-K{row['wfo']}-"
                    f"{row2['phenomena']}-{row2['significance']}-"
                    f"{row2['eventid']:04.0f}"
                )
                products += (
                    f'<a href="{url}">'
                    f'{get_ps_string(row2["phenomena"], row2["significance"])}'
                    f' {row2["eventid"]}</a><br />'
                )
            if products == "":
                products = "No Warnings Found"
            lsrdf.at[idx, "prodlinks"] = products


@iemapp(
    content_type="application/vnd.geo+json",
    help=__doc__,
    schema=Schema,
    parse_times=False,
)
def application(environ, start_response):
    """Do Something"""
    # Quirk unhandled properly yet
    environ["wfos"] = list(filter(lambda x: len(x) == 3, environ["wfos"]))
    environ["states"] = list(filter(lambda x: len(x) == 2, environ["states"]))
    # Go Main Go
    headers = [("Content-type", "application/vnd.geo+json")]
    if environ["phenomena"] is not None:
        lsrdf = do_vtec(environ)
    elif environ["states"]:
        lsrdf = do_states(environ)
    else:
        lsrdf = do_default(environ)
    if environ["inc_ap"]:
        add_warnings(lsrdf)
    # legacy stuff
    lsrdf["st"] = lsrdf["state"]
    lsrdf = lsrdf.rename(
        columns={
            "iso_valid": "valid",
        }
    )
    # Keep magnitude as a string
    lsrdf["magnitude"] = ""
    lsrdf.loc[lsrdf["magf"].isna(), "magnitude"] = ""
    lsrdf.loc[lsrdf["magf"].notna(), "magnitude"] = lsrdf["magf"].astype(str)
    # Trim any strings ending in .0
    lsrdf["magnitude"] = lsrdf["magnitude"].str.replace(
        r"\.0$", "", regex=True
    )
    start_response("200 OK", headers)
    return [lsrdf.to_json().encode("ascii")]
