""".. title:: Retrieve NWS Text Products

Documentation for /cgi-bin/afos/retrieve.py
-------------------------------------------

This service returns NWS Text Products from the IEM's database.  The database
updates in near real-time, so it should be considered a near real-time source
with minimal latency.

Changelog
~~~~~~~~~

- 2024-03-29: Initial documentation release and migrate to a pydantic schema
  verification.

Examples
~~~~~~~~

Return all TORnado warnings issued between 20 and 21 UTC on 27 Apr 2011 as
a zip file.

  https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?\
sdate=2011-04-27T20:00Z&edate=2011-04-27T21:00Z&pil=TOR&fmt=zip&limit=9999

Return the last Area Forecast Discussion from NWS Des Moines as text

  https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX

"""

import zipfile
from datetime import datetime, timedelta, timezone
from io import BytesIO, StringIO
from typing import Optional, Union

from pydantic import Field, field_validator
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import html_escape, utc
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

WARPIL = "FLS FFS AWW TOR SVR FFW SVS LSR SPS WSW FFA WCN NPW".split()


class MyModel(CGIModel):
    """See how we are called."""

    center: str = Field(
        "",
        description=(
            "The 4 character source iddentifier to limit the search to. "
            "This is typically only used when a PIL is ambiguous"
        ),
        max_length=4,
    )
    dl: bool = Field(
        False,
        description=(
            "If set to 1, the returned data will be downloaded as a file"
        ),
    )
    edate: Optional[Union[None, datetime]] = Field(
        None,
        description=(
            "The ending timestamp in UTC to limit the database search. This "
            "value is exclusive."
        ),
    )
    fmt: str = Field(
        "text",
        description=(
            "The format of the returned data, either text, html, or zip. The "
            "meaning of ``text`` is to return something that resembles what "
            "would have been sent over the NWS NOAAPort system. The ``html`` "
            "format is a bit more human readable. The ``zip`` format will "
            "return a zip file containing the text products, one file per "
            "product."
        ),
        pattern="^(text|html|zip)$",
    )
    limit: int = Field(
        1,
        description=(
            "The number of products to return, default is 1. This number "
            "is limited to 9999."
        ),
        ge=1,
        le=9999,
    )
    pil: ListOrCSVType = Field(
        ...,
        description=(
            "The 3 to 6 character AFOS ID / Product ID to query for. This is "
            "typically the third line of a NWS Text Product"
        ),
    )
    sdate: Optional[Union[None, datetime]] = Field(
        None,
        description=(
            "The starting timestamp in UTC to limit the database search. This "
            "value is inclusive."
        ),
    )
    ttaaii: str = Field(
        "",
        description=(
            "The 6 character WMO Header to limit the search to.  This is "
            "typically only used when a PIL is ambiguous"
        ),
    )

    @field_validator("sdate", "edate", mode="before")
    def allow_str_or_none(cls, v):
        return None if v == "" else v


def pil_logic(pils):
    """Convert the CGI pil value into something we can query."""
    # Convert to uppercase
    pils = [s.upper() for s in pils]
    res = []
    for pil in pils:
        if pil[:3] == "WAR":
            for q in WARPIL:
                res.append(f"{q}{pil[3:6]}")  # noqa
        else:
            # whitespace pad
            res.append(f"{pil.strip():6.6s}")
    return res


def zip_handler(cursor):
    """Stream back a zipfile!"""
    bio = BytesIO()
    with zipfile.ZipFile(bio, "w") as zfp:
        for row in cursor:
            zfp.writestr(f"{row[1]}_{row[2]}.txt", row[0])
    bio.seek(0)
    return [bio.getvalue()]


def special_metar_logic(pils, limit, fmt, sio):
    access = get_dbconn("iem")
    cursor = access.cursor()
    sql = (
        "SELECT raw from current_log c JOIN stations t on "
        "(t.iemid = c.iemid) WHERE raw != '' and "
        f"id = '{pils[0][3:].strip()}' ORDER by valid DESC LIMIT {limit}"
    )
    cursor.execute(sql)
    for row in cursor:
        if fmt == "html":
            sio.write("<pre>\n")
        else:
            sio.write("\001\n")
        if fmt == "html":
            sio.write(html_escape(row[0].replace("\r\r\n", "\n")))
        else:
            sio.write(row[0].replace("\r\r\n", "\n"))
        if fmt == "html":
            sio.write("</pre>\n")
        else:
            sio.write("\003\n")
    if cursor.rowcount == 0:
        sio.write(f"ERROR: METAR lookup for {pils[0][3:].strip()} failed")
    cursor.close()
    access.close()
    return [sio.getvalue().encode("ascii", "ignore")]


@iemapp(help=__doc__, schema=MyModel, parse_times=False)
def application(environ, start_response):
    """Process the request"""
    # Expand PILs
    pils = pil_logic(environ["pil"])
    # Establish our date range
    if environ["sdate"] is None:
        environ["sdate"] = utc(1980)
    else:
        environ["sdate"] = environ["sdate"].replace(tzinfo=timezone.utc)
    if environ["edate"] is None:
        environ["edate"] = utc() + timedelta(days=1)
    else:
        environ["edate"] = environ["edate"].replace(tzinfo=timezone.utc)
    if environ["edate"] < environ["sdate"]:
        environ["sdate"], environ["edate"] = environ["edate"], environ["sdate"]
    fmt = environ["fmt"]
    headers = [("X-Content-Type-Options", "nosniff")]
    if environ["dl"] or fmt == "zip":
        suffix = "zip" if fmt == "zip" else "txt"
        headers.append(("Content-type", "application/octet-stream"))
        headers.append(
            ("Content-disposition", f"attachment; filename=afos.{suffix}")
        )
    else:
        if fmt == "text":
            headers.append(("Content-type", "text/plain"))
        elif fmt == "html":
            headers.append(("Content-type", "text/html"))
    start_response("200 OK", headers)

    sio = StringIO()
    if pils[0][:3] == "MTR":
        return special_metar_logic(pils, environ["limit"], fmt, sio)

    params = {
        "pils": pils,
        "center": environ["center"],
        "edate": environ["edate"],
        "ttaaii": environ["ttaaii"],
        "limit": environ["limit"],
    }
    centerlimit = "" if environ["center"] == "" else " and source = :center "
    ttlimit = "" if environ["ttaaii"] == "" else " and wmo = :ttaaii "
    plimit = " pil = ANY(:pils) "
    if len(pils) == 1:
        plimit = " pil = :pil "
        params["pil"] = pils[0].strip()
        if len(pils[0].strip()) == 3:
            # There's a database index on this
            plimit = " substr(pil, 1, 3) = :pil "
    sql = (
        "SELECT data, pil, "
        "to_char(entered at time zone 'UTC', 'YYYYMMDDHH24MI') as ts "
        f"from products WHERE {plimit} "
        f"and entered >= :sdate and entered <= :edate {centerlimit} "
        f"{ttlimit} ORDER by entered DESC LIMIT :limit"
    )
    # Query optimization when sdate is very old and perhaps we could reach
    # the limit by looking at the last 31 days of data
    sdates = [environ["sdate"]]
    if environ["sdate"] < (environ["edate"] - timedelta(days=365)):
        sdates = [utc() - timedelta(days=31), environ["sdate"]]
    with get_sqlalchemy_conn("afos") as conn:
        for sdate in sdates:
            params["sdate"] = sdate
            cursor = conn.execute(text(sql), params)
            if cursor.rowcount == environ["limit"]:
                break

        if fmt == "zip":
            return zip_handler(cursor)

        for row in cursor:
            if fmt == "html":
                sio.write(
                    f'<a href="/wx/afos/p.php?pil={row[1]}&e={row[2]}">'
                    "Permalink</a> for following product: "
                )
                sio.write("<br /><pre>\n")
            else:
                sio.write("\001\n")
            # Remove control characters from the product as we are including
            # them manually here...
            if fmt == "html":
                sio.write(
                    html_escape(row[0])
                    .replace("\003", "")
                    .replace("\001\r\r\n", "")
                    .replace("\r\r\n", "\n")
                )
            else:
                sio.write(
                    (row[0])
                    .replace("\003", "")
                    .replace("\001\r\r\n", "")
                    .replace("\r\r\n", "\n")
                )
            if fmt == "html":
                sio.write("</pre><hr>\n")
            else:
                sio.write("\n\003\n")

        if cursor.rowcount == 0:
            sio.write(f"ERROR: Could not Find: {','.join(pils)}")
    return [sio.getvalue().encode("ascii", "ignore")]
