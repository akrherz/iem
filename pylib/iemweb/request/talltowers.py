""".. title:: Tall Towers Data Request

Return to `API Services </api/#cgi>`_ or
`Download Frontend </projects/iao/analog_download.php>`_

Changelog
---------

- 2024-09-02: Initial documentation update and pydantic validation

"""

from datetime import timedelta
from io import BytesIO, StringIO

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

TOWERIDS = {0: "ETTI4", 1: "MCAI4"}


class Schema(CGIModel):
    """See how we are called."""

    agg: ListOrCSVType = Field(
        default=["avg"],
        description="Aggregation method to use",
    )
    format: str = Field(
        default="excel",
        description="The format of the response",
        pattern="^(excel|tdf|comma)$",
    )
    ets: AwareDatetime = Field(
        default=None,
        description="End of the period of interest",
    )
    sts: AwareDatetime = Field(
        default=None,
        description="Start of the period of interest",
    )
    station: ListOrCSVType = Field(..., description="Station(s) to query")
    var: ListOrCSVType = Field(
        ...,
        description="Variable(s) to query",
    )
    window: int = Field(
        default=1,
        description="Window size for aggregation",
        ge=1,
        le=1440,
    )
    z: ListOrCSVType = Field(..., description="Height(s) to query")
    tz: str = Field(default="Etc/UTC", description="Timezone to use")
    year1: int = Field(None, description="Start Year, if sts not provided")
    month1: int = Field(None, description="Start Month, if sts not provided")
    day1: int = Field(None, description="Start Day, if sts not provided")
    hour1: int = Field(None, description="Start Hour, if sts not provided")
    year2: int = Field(None, description="End Year, if ets not provided")
    month2: int = Field(None, description="End Month, if ets not provided")
    day2: int = Field(None, description="End Day, if ets not provided")
    hour2: int = Field(None, description="End Hour, if ets not provided")


def get_stations(environ):
    """Figure out the requested station"""
    towers = []
    for tid, nwsli in TOWERIDS.items():
        if nwsli in environ["station"]:
            towers.append(tid)

    return towers


def get_columns(cursor):
    """What have we here."""
    cursor.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name   = 'data_analog'"
    )
    res = [row[0] for row in cursor]
    return res


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go main Go"""
    pgconn = get_dbconn("talltowers")
    columns = get_columns(pgconn.cursor())
    tzname = environ["tz"]

    stations = get_stations(environ)
    if not stations:
        raise IncompleteWebRequest("No stations")
    sts = environ["sts"]
    ets = environ["ets"]
    if (ets - sts) > timedelta(days=31):
        ets = sts + timedelta(days=31)
    fmt = environ["format"]
    # Build out our variable list
    tokens = []
    zz = environ["z"]
    varnames = environ["var"]
    aggs = environ["agg"]
    for z in zz:
        for v in varnames:
            v1 = v
            v2 = ""
            if v.find("_") > -1:
                v1, v2 = v.split("_")
                v2 = f"_{v2}"
            colname = f"{v1}_{z}m{v2}"
            if colname not in columns:
                continue
            for agg in aggs:
                tokens.append(f"{agg}({colname}) as {colname}_{agg}")  # noqa

    tw = environ["window"]

    sql = f"""
    SELECT tower,
    (date_trunc('hour', valid) +
    (((date_part('minute', valid)::integer / {tw}::integer) * {tw}::integer)
     || ' minutes')::interval) at time zone :tz as ts,
    {','.join(tokens)} from
    data_analog where tower = ANY(:sids) and valid >= :sts and valid < :ets
    GROUP by tower, ts ORDER by tower, ts
    """
    with get_sqlalchemy_conn("talltowers") as conn:
        df = pd.read_sql(
            text(sql),
            conn,
            params={"tz": tzname, "sids": stations, "sts": sts, "ets": ets},
        )
    df = df.rename(columns={"ts": "valid"})
    df["tower"] = df["tower"].replace(TOWERIDS)
    pgconn.close()
    if fmt in ["tdf", "comma"]:
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment; filename=talltowers.txt"),
        ]
        start_response("200 OK", headers)
        sio = StringIO()
        df.to_csv(sio, sep="," if fmt == "comma" else "\t", index=False)
        return [sio.getvalue().encode("utf8")]

    # Excel
    bio = BytesIO()
    # pylint: disable=abstract-class-instantiated
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Data", index=False)
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=talltowers.xlsx"),
    ]
    start_response("200 OK", headers)
    return [bio.getvalue()]
