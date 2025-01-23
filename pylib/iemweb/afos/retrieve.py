""".. title:: Retrieve NWS Text Products

Return to `API Services </api/>`_ or
`NWS Text Products Interface </wx/afos/>`_.

Documentation for /cgi-bin/afos/retrieve.py
-------------------------------------------

This service returns NWS Text Products from the IEM's database.  The database
updates in near real-time, so it should be considered a near real-time source
with minimal latency.

Changelog
~~~~~~~~~

- 2025-01-22: Added `aviation_afd` flag for the specific case of retrieving
  the "Aviation" section of an Area Forecast Discussion.
- 2025-01-08: Added some caching due to incessant requests for the same data.
- 2024-08-25: Add ``order`` parameter to allow for order of the returned
  products.
- 2024-03-29: Initial documentation release and migrate to a pydantic schema
  verification.

Examples
~~~~~~~~

Return all of the Daily Summary Messages for Des Moines from 1 Jan 2025 to 9
Jan 2025 in text format.

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?\
limit=9999&pil=DSMDSM&fmt=text&sdate=2025-01-01&edate=2025-01-09

Return all TORnado warnings issued between 20 and 21 UTC on 27 Apr 2011 as
a zip file.

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?\
sdate=2011-04-27T20:00Z&edate=2011-04-27T21:00Z&pil=TOR&fmt=zip&limit=9999

Return the last Area Forecast Discussion from NWS Des Moines as text

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX

Retrieve recent METAR observations for KDSM, note that this only works for
recent data, no archive support with this API.

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=MTRDSM

Use the WAR pil shortcut to retrieve a number of Des Moines products

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=WARDSM

Return the last AFDDMX product in text format

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX&fmt=text

Return a zip file of AFDDMX products during 2024

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX&fmt=zip&\
sdate=2024-01-01T00:00Z&edate=2024-12-31T23:59Z

Return the aviation section of the latest AFD from NWS Des Moines

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX&\
aviation_afd=1

"""

import re
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
AVIATION_AFD = re.compile(r"^\.AVIATION[\s\.]", re.IGNORECASE | re.MULTILINE)


class MyModel(CGIModel):
    """See how we are called."""

    aviation_afd: bool = Field(
        False,
        description=(
            "If set to 1, the returned data will be the 'Aviation' section "
            "of an Area Forecast Discussion. This requires the PIL to be "
            "an AFD product and a limit of 1 set."
        ),
    )
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
            "typically the third line of a NWS Text Product.  A special case "
            f"of ``WAR`` will return {', '.join(WARPIL)} products."
        ),
    )
    sdate: Optional[Union[None, datetime]] = Field(
        None,
        description=(
            "The starting timestamp in UTC to limit the database search. This "
            "value is inclusive."
        ),
    )
    order: str = Field(
        default="desc",
        description=(
            "The order of the returned products, either 'asc' or 'desc'"
        ),
        pattern="^(asc|desc)$",
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
        """pydantic can't seem to handle this."""
        # pydantic/pydantic/issues/9308
        if 8 <= len(v) < 10:
            # zero pad
            return "-".join(f"{int(v):02.0f}" for v in v.split("-"))
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


def special_metar_logic(pils, limit, fmt, sio, order):
    access = get_dbconn("iem")
    cursor = access.cursor()
    sql = (
        "SELECT raw from current_log c JOIN stations t on "
        "(t.iemid = c.iemid) WHERE raw != '' and "
        f"id = '{pils[0][3:].strip()}' ORDER by valid {order} LIMIT {limit}"
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


def get_mckey(environ: dict) -> Optional[str]:
    """Cache a specific request."""
    # limit=9999&pil=DSMDEN&fmt=text&sdate=2025-01-07&edate=2025-01-09
    if (
        environ["pil"][0].startswith("DSM")
        and environ["fmt"] == "text"
        and environ["sdate"] is not None
        and environ["edate"] is not None
    ):
        return (
            f"afos_retrieve.py_{environ['pil'][0]}_{environ['sdate']:%Y%m%d}_"
            f"{environ['edate']:%Y%m%d}_{environ['limit']}"
        )
    return None


def get_ct(environ: dict) -> str:
    """Figure out the content type."""
    fmt = environ["fmt"]
    if fmt == "zip" or environ["dl"]:
        return "application/octet-stream"
    if fmt == "html":
        return "text/html"
    return "text/plain"


@iemapp(
    help=__doc__,
    schema=MyModel,
    memcacheexpire=600,
    memcachekey=get_mckey,
    content_type=get_ct,
    parse_times=False,
)
def application(environ, start_response):
    """Process the request"""
    order = environ["order"]
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
    headers.append(("Content-type", get_ct(environ)))
    if environ["dl"] or fmt == "zip":
        suffix = "zip" if fmt == "zip" else "txt"
        headers.append(
            ("Content-disposition", f"attachment; filename=afos.{suffix}")
        )
    start_response("200 OK", headers)

    sio = StringIO()
    if pils[0][:3] == "MTR":
        return special_metar_logic(pils, environ["limit"], fmt, sio, order)

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
        f"{ttlimit} ORDER by entered {order} LIMIT :limit"
    )
    # Query optimization when sdate is very old and perhaps we could reach
    # the limit by looking at the last 31 days of data
    sdates = [environ["sdate"]]
    if environ["sdate"] < (environ["edate"] - timedelta(days=365)) and (
        order == "desc"
    ):
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
            payload = row[0]
            if (
                len(pils) == 1
                and pils[0].startswith("AFD")
                and environ["aviation_afd"]
            ):
                # Special case for AFD products, we only want the Aviation
                # section
                parts = payload.split("&&")
                for part in parts:
                    if AVIATION_AFD.search(part):
                        payload = part
                        break
            # Remove control characters from the product as we are including
            # them manually here...
            if fmt == "html":
                sio.write(
                    html_escape(payload)
                    .replace("\003", "")
                    .replace("\001\r\r\n", "")
                    .replace("\r\r\n", "\n")
                )
            else:
                sio.write(
                    payload.replace("\003", "")
                    .replace("\001\r\r\n", "")
                    .replace("\r\r\n", "\n")
                )
            if fmt == "html":
                sio.write("</pre><hr>\n")
            else:
                sio.write("\n\003\n")

        if cursor.rowcount == 0:
            sio.write(f"ERROR: Could not Find: {','.join(pils)}")
    return sio.getvalue()
