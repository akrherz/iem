"""JSON service emitting observation history for a given date"""

import datetime
import json

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import IEMVARS
from pyiem.util import html_escape
from pyiem.webutil import CGIModel, iemapp
from pymemcache.client import Client


class Schema(CGIModel):
    """See how we are called."""

    station: str = Field(
        ...,
        description="The station identifier to query for",
        pattern=r"^[A-Z0-9\-]*$",
    )
    network: str = Field(
        ...,
        description="The network identifier to query for",
        pattern="^[A-Z0-9_]*$",
    )
    date: datetime.date = Field(
        ...,
        description="The date to query for",
    )
    cb: str = Field(None, description="Callback function for JSONP output")


def do_today(table, station, network, date):
    """Our backend is current_log"""
    cols = ["local_valid", "utc_valid", "tmpf", "sknt", "gust", "drct"]
    table["fields"] = [IEMVARS[col] for col in cols]
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
            select
            to_char(valid at time zone tzname,
                    'YYYY-MM-DDThh24:MI:SS') as local_valid,
            to_char(valid at time zone 'UTC',
                    'YYYY-MM-DDThh24:MI:SSZ') as utc_valid,
            tmpf, sknt, gust, drct from current_log c JOIN stations t
            on (c.iemid = t.iemid) WHERE date(valid at time zone tzname) = %s
            and t.id = %s and t.network = %s ORDER by local_valid
        """,
            conn,
            params=(date, station, network),
            index_col=None,
        )
    table["rows"] = list(df.itertuples(index=False))


def do_asos(table, station, _network, date):
    """Our backend is ASOS"""
    cols = ["local_valid", "utc_valid", "tmpf", "sknt", "gust", "drct"]
    table["fields"] = [IEMVARS[col] for col in cols]
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
            select
            to_char(valid at time zone tzname,
                    'YYYY-MM-DDThh24:MI:SS') as local_valid,
            to_char(valid at time zone 'UTC',
                    'YYYY-MM-DDThh24:MI:SSZ') as utc_valid,
            tmpf, sknt, gust, drct from alldata a JOIN stations t
            on (a.station = t.id) WHERE date(valid at time zone tzname) = %s
            and station = %s ORDER by local_valid
        """,
            conn,
            params=(date, station),
            index_col=None,
        )
    table["rows"] = list(df.itertuples(index=False))


def workflow(station, network, date):
    """Go get the dictionary of data we need and deserve"""
    table = {"fields": [], "rows": []}
    if date == datetime.date.today():
        do_today(table, station, network, date)
    elif network.find("ASOS") > -1:
        do_asos(table, station, network, date)

    return json.dumps(table)


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    station = environ["station"]
    network = environ["network"]
    date = environ["date"]

    mckey = f"/json/obhistory/{station}/{network}/{date}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = workflow(station, network, date).replace("NaN", "null")
        mc.set(mckey, res, 3600)
    else:
        res = res.decode("utf-8")
    mc.close()
    if environ["cb"] is not None:
        res = f"{html_escape(environ['cb'])}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
