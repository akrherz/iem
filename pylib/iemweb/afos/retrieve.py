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

- 2026-06-09: The `pil` needs to be ASCII characters.
- 2026-05-07: The `center` parameter needs to be uppercase and four chars.
- 2026-04-30: An internal service rewrite was done attempting to remove some
  very slow edge query cases.  Please let me know of any variances you find.
- 2026-04-21: Due to incessant requests made against this service, a 1 second
  per remote IP address throttle is in place for DSM requests.
- 2026-03-13: After gnashing of teeth about the METARs, a compromise was
  reached to return only the latest non-MADISHF METAR when requesting just
  one, but return anything available when requesting more than 1.  Will likely
  regret this decision as well.
- 2026-03-09: The METAR service was updated to not consider the IEM generated
  METARs based on the MADIS HF feed.

Examples
~~~~~~~~

Return all of the Daily Summary Messages for Des Moines from 1 Jan 2025 to 9
Jan 2025 in text format.

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?\
limit=9999&pil=DSMDSM&fmt=text&sdate=2025-01-01&edate=2025-01-09

Return the last 5 Daily Summary Messages for Des Moines in text format.

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?\
limit=5&pil=DSMDSM&fmt=text

Same request, but in HTML format:

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?\
limit=1&pil=DSMDSM&fmt=html

Return all TORnado warnings issued between 20 and 21 UTC on 27 Apr 2011 as
a zip file.

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?\
sdate=2011-04-27T20:00Z&edate=2011-04-27T21:00Z&pil=TOR&fmt=zip&limit=9999

Return the last Area Forecast Discussion from NWS Des Moines as text

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX

Retrieve recent METAR observations for KDSM, note that this only works for
recent data, no archive support with this API.

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=MTRDSM

Same request, but in HTML format:

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=MTRDSM&fmt=html

Use the WAR pil shortcut to retrieve a number of Des Moines products

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=WARDMX

Return the last AFDDMX product in text format

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX&fmt=text

Same request, but in HTML format:

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX&fmt=html

Return a zip file of AFDDMX products during 2024

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX&fmt=zip&\
sdate=2024-01-01T00:00Z&edate=2024-12-31T23:59Z

Return the aviation section of the latest AFD from NWS Des Moines

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX&\
aviation_afd=1

Same request, but HTML format this time.

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX&\
aviation_afd=1&fmt=html

Return the LAV MOS for KATL by specifying that KATL should appear within the
product text, so to not return the mos for PATL.

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=LAVATL&\
matches=KATL

Return the first AFDDMX during the 2024+2025 period

https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=AFDDMX&\
fmt=text&sdate=2024-01-01T00:00Z&edate=2025-12-31T23:59Z&limit=1&order=asc

"""

import re
import zipfile
from datetime import datetime, timedelta, timezone
from io import BytesIO, StringIO
from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import html_escape, utc
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy.engine import Connection
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.expression import TextClause

from iemweb import error_log
from iemweb.util import get_ct

AFOS_RE = re.compile(r"^[A-Z0-9]{3,6}$", re.IGNORECASE)
WARPIL = "FLS FFS AWW TOR SVR FFW SVS LSR SPS WSW FFA WCN NPW".split()
AVIATION_AFD = re.compile(r"^\.AVIATION[\s\.]", re.IGNORECASE | re.MULTILINE)
STATEMENT_TIMEOUT: str = "60s"


class Schema(CGIModel):
    """See how we are called."""

    aviation_afd: Annotated[
        bool,
        Field(
            description=(
                "If set to 1, the returned data will be the 'Aviation' "
                "section of an Area Forecast Discussion. This requires the "
                "PIL to be an AFD product and a limit of 1 set."
            ),
        ),
    ] = False
    center: Annotated[
        str,
        Field(
            description=(
                "The 4 character source iddentifier to limit the search to. "
                "This is typically only used when a PIL is ambiguous like in "
                "the case of Alaska three character ids conflicting with "
                "CONUS.  This is not required."
            ),
            pattern=r"^[A-Z]{4}$",
        ),
    ] = ""
    dl: Annotated[
        bool,
        Field(
            description=(
                "If set to 1, the returned data will be downloaded as a file"
            ),
        ),
    ] = False
    edate: Annotated[
        datetime,
        Field(
            description=(
                "The ending timestamp in UTC to limit the database search. "
                "This value is exclusive."
            ),
            default_factory=lambda: utc() + timedelta(days=1),
        ),
    ]
    fmt: Annotated[
        str,
        Field(
            description=(
                "The format of the returned data, either text, html, or zip. "
                "The meaning of ``text`` is to return something that "
                "resembles what would have been sent over the NWS NOAAPort "
                "system. The ``html`` format is a bit more human readable. "
                "The ``zip`` format will return a zip file containing the "
                "text products, one file per product. The ``zip`` format is "
                "not supported for the one-off ``MTR`` METAR service."
            ),
            pattern="^(text|html|zip)$",
        ),
    ] = "text"
    limit: Annotated[
        int,
        Field(
            description=(
                "The number of products to return, default is 1. This number "
                "is limited to 9999."
            ),
            ge=1,
            le=9999,
        ),
    ] = 1
    matches: Annotated[
        str,
        Field(
            description=(
                "Attempt a simple substring search within candidate products "
                "for the given exact string.  This is limited functionality "
                "for now."
            ),
            max_length=4,
            min_length=4,
        ),
    ] = None
    pil: Annotated[
        ListOrCSVType,
        Field(
            description=(
                "The 3 to 6 character AFOS ID / Product ID to query for. This "
                "is typically the third line of a NWS Text Product.  A "
                f"special case of ``WAR`` will return {', '.join(WARPIL)} "
                "products. If you provide a single PIL that is 3 characters "
                "in length, it will be used as a first three pil character "
                "match."
            ),
        ),
    ]
    sdate: Annotated[
        datetime,
        Field(
            description=(
                "The starting timestamp in UTC to limit the database search. "
                "This value is inclusive."
            ),
        ),
    ] = utc(1980)
    order: Annotated[
        str,
        Field(
            description=(
                "The order of the returned products, either 'asc' or 'desc'"
            ),
            pattern="^(asc|desc)$",
        ),
    ] = "desc"
    ttaaii: Annotated[
        str,
        Field(
            description=(
                "The 6 character WMO Header to limit the search to.  This is "
                "typically only used when a PIL is ambiguous"
            ),
            max_length=6,
        ),
    ] = ""

    @field_validator("pil", mode="after")
    @classmethod
    def rectify_pils(cls, pils: list[str]):
        """Apply some sanitization."""
        pils = [val.strip().upper() for val in pils]
        res = []
        for pil in pils:
            if not AFOS_RE.match(pil):
                raise ValueError(f"Invalid PIL: {pil}")
            # Lame WAR alias
            if pil.startswith("WAR") and len(pil) == 6:
                res.extend(f"{q}{pil[3:6]}" for q in WARPIL)
                continue
            res.append(pil)
        return res

    @field_validator("sdate", "edate", mode="before")
    @classmethod
    def rectify_datestr(cls, v: str):
        """pydantic can't seem to handle this."""
        # pydantic/pydantic/issues/9308
        if 8 <= len(v) < 10:
            # zero pad
            return "-".join(f"{int(v):02.0f}" for v in v.split("-"))
        return v

    @model_validator(mode="after")
    def rectify_model(self):
        """Apply some business logic to what the user provided.."""
        self.sdate = (
            self.sdate.replace(tzinfo=timezone.utc)
            if self.sdate.tzinfo is None
            else self.sdate.astimezone(timezone.utc)
        )
        self.edate = (
            self.edate.replace(tzinfo=timezone.utc)
            if self.edate.tzinfo is None
            else self.edate.astimezone(timezone.utc)
        )
        if self.edate < self.sdate:
            self.sdate, self.edate = self.edate, self.sdate
        return self


def zip_handler(rows: list[tuple]) -> bytes:
    """Stream back a zipfile!"""
    bio = BytesIO()
    with zipfile.ZipFile(bio, "w") as zfp:
        for row in rows:
            zfp.writestr(f"{row[1]}_{row[2]}.txt", row[0])
    bio.seek(0)
    return bio.getvalue()


def special_metar_logic(conn: Connection, request: Schema):
    """Special METAR logic."""
    metar_id = request.pil[0][3:].strip()
    params = {"pil": metar_id, "limit": request.limit}
    extra = "and strpos(raw, 'MADISHF') = 0" if request.limit == 1 else ""
    sql = sql_helper(
        "SELECT raw from current_log c JOIN stations t on "
        "(t.iemid = c.iemid) WHERE raw != '' {extra} "
        "and id = :pil "
        "ORDER by valid {order} LIMIT :limit",
        order=request.order,
        extra=extra,
    )
    res = conn.execute(sql, params)
    sio = StringIO()
    for row in res:
        sio.write("<pre>\n" if request.fmt == "html" else "\001\n")
        if request.fmt == "html":
            sio.write(html_escape(row[0].replace("\r\r\n", "\n")))
        else:
            sio.write(row[0].replace("\r\r\n", "\n"))
        if request.fmt == "html":
            sio.write("</pre>\n")
        else:
            sio.write("\003\n")
    # Turns out that res.rowcount is not reliable
    if sio.tell() == 0:
        sio.write(f"ERROR: METAR lookup for {metar_id} failed")
    return sio.getvalue()


def get_mckey(environ: dict) -> str | None:
    """Cache a specific request."""
    # Get reference to request
    request: Schema = environ["_cgimodel_schema"]
    # limit=9999&pil=DSMDEN&fmt=text&sdate=2025-01-07&edate=2025-01-09
    if request.pil[0].startswith("DSM") and request.fmt == "text":
        return (
            f"afos_retrieve.py_{request.pil[0]}_{request.sdate:%Y%m%d}_"
            f"{request.edate:%Y%m%d}_{request.limit}"
        )
    return None


def get_ip_throttle_secs(environ: dict) -> int:
    """Figure out what the throttle is."""
    query: Schema = environ["_cgimodel_schema"]
    if any(pil.startswith("DSM") for pil in query.pil):
        return 1
    return 0


def chunk_dates(request: Schema) -> tuple[list[datetime], list[datetime]]:
    """Partition up the requested period into chunks to iterate through."""
    # Shortcut refs
    sd = request.sdate
    ed = request.edate
    order = request.order
    total_days = (ed - sd).days
    # If the request is already inside 367 days, lets not bother
    if total_days < 367:
        return [sd], [ed]
    sdates = []
    edates = []
    # time chunks to iterate through from the start to finish
    now = sd if order == "asc" else ed
    multiplier = 1
    while sd <= now <= ed:
        step = 31 if multiplier == 1 else 365
        if order == "asc":
            sdates.append(now)
            now += timedelta(days=multiplier * step)
            edates.append(min(now, ed))
        else:
            edates.append(now)
            now -= timedelta(days=multiplier * step)
            sdates.append(max(now, sd))
        multiplier += 3

    return sdates, edates


def do_query_work(
    conn: Connection, request: Schema, sql: TextClause, params: dict
) -> list[tuple]:
    """Do the database query and processing."""
    # Create a series of datetime chunks to iterate through
    sdates, edates = chunk_dates(request)

    # For better or worse, we are storing this in memory, but we limit to 9999
    rows = []
    for sdate, edate in zip(sdates, edates, strict=True):
        params["sdate"] = sdate
        params["edate"] = edate
        cursor = conn.execute(sql, params)
        rows.extend(cursor.fetchall())
        if len(rows) >= request.limit:
            rows = rows[: request.limit]
            break

    return rows


def html_handler(rows: list[tuple], afd_logic: bool) -> str:
    """Handle conversion to HTML."""
    sio = StringIO()
    for row in rows:
        sio.write(
            f'<a href="/wx/afos/p.php?pil={row[1]}&e={row[2]}">'
            "Permalink</a> for following product: "
        )
        sio.write("<br /><pre>\n")
        payload = row[0]
        if afd_logic:
            # Special case for AFD products, we only want the Aviation
            # section
            parts = payload.split("&&")
            for part in parts:
                if AVIATION_AFD.search(part):
                    payload = part
                    break
        # Remove control characters from the product as we are including
        # them manually here...
        sio.write(
            html_escape(payload)
            .replace("\003", "")
            .replace("\001", "")
            .replace("\r", "")
        )
        sio.write("</pre><hr>\n")
    return sio.getvalue()


def text_handler(rows: list[tuple], afd_logic: bool) -> str:
    """Handle text output."""
    sio = StringIO()
    for row in rows:
        sio.write("\001\n")
        payload = row[0]
        if afd_logic:
            # Special case for AFD products, we only want the Aviation
            # section
            parts = payload.split("&&")
            for part in parts:
                if AVIATION_AFD.search(part):
                    payload = part
                    break
        sio.write(
            payload.replace("\003", "").replace("\001", "").replace("\r", "")
        )
        sio.write("\n\003\n")
    return sio.getvalue()


@iemapp(
    help=__doc__,
    schema=Schema,
    memcacheexpire=600,
    memcachekey=get_mckey,
    content_type=get_ct,
    parse_times=False,
    ip_throttle_secs=get_ip_throttle_secs,
)
def application(environ: dict, start_response: callable):
    """Process the request."""
    # Capture the client request params
    request: Schema = environ["_cgimodel_schema"]
    headers = [
        ("X-Content-Type-Options", "nosniff"),
        ("Content-type", get_ct(environ)),
    ]
    if request.dl or request.fmt == "zip":
        suffix = "zip" if request.fmt == "zip" else "txt"
        headers.append(
            ("Content-disposition", f"attachment; filename=afos.{suffix}")
        )

    if request.pil[0].startswith("MTR"):
        if request.fmt == "zip":
            start_response(
                "422 Unprocessable Entity",
                [("Content-type", "text/plain")],
            )
            return "ERROR: The zip format is not supported for the MTR service"
        with get_sqlalchemy_conn("iem") as conn:
            start_response("200 OK", headers)
            return special_metar_logic(conn, request)

    params = {
        "pils": request.pil,
        "center": request.center,
        "edate": request.edate,
        "ttaaii": request.ttaaii,
        "limit": request.limit,
        "matches": request.matches,
    }
    centerlimit = "" if request.center == "" else " and source = :center "
    ttlimit = "" if request.ttaaii == "" else " and wmo = :ttaaii "
    plimit = " pil = ANY(:pils) "
    mlimit = " and strpos(data, :matches) > 0 " if request.matches else ""
    if len(request.pil) == 1:
        plimit = " pil = :pil "
        params["pil"] = request.pil[0]
        if len(request.pil[0]) == 3:
            # Serious perf issues here.  substr partial index confuses planner
            # LIKE also triggers filtering, the goose here is to force a
            # index
            pil3 = request.pil[0]
            # for example, pil3=AFD then next_char is E and we have `AFE`
            next_char = chr(ord(pil3[2]) + 1)
            params["pil2"] = f"{pil3[:2]}{next_char}"
            plimit = " pil >= :pil and pil < :pil2 "
    sql = sql_helper(
        "SELECT data, pil, "
        "to_char(entered at time zone 'UTC', 'YYYYMMDDHH24MI') as ts "
        "from products WHERE {plimit} "
        "and entered >= :sdate and entered < :edate {centerlimit} "
        "{ttlimit} {mlimit} ORDER by entered {order} LIMIT :limit",
        plimit=plimit,
        centerlimit=centerlimit,
        ttlimit=ttlimit,
        order=request.order,
        mlimit=mlimit,
    )
    with get_sqlalchemy_conn("afos") as conn:
        # Prevent something from running away with resources
        # Lovely situation here without parameter support for ``set``
        conn.execute(
            sql_helper(
                "SET statement_timeout = '{timeout}'",
                timeout=STATEMENT_TIMEOUT,
            )
        )
        # So the below could time out
        try:
            rows = do_query_work(conn, request, sql, params)
        except OperationalError as exp:
            error_log(environ, str(exp))
            start_response(
                "503 Service Unavailable", [("Content-type", "text/plain")]
            )
            return "ERROR: Query took too long to complete"

    start_response("200 OK", headers)

    if request.fmt == "zip":
        return zip_handler(rows)

    if not rows:
        return f"ERROR: Could not Find: {','.join(request.pil)}"

    afd_logic = (
        len(request.pil) == 1
        and request.pil[0].startswith("AFD")
        and request.aviation_afd
    )

    if request.fmt == "html":
        return html_handler(rows, afd_logic)

    return text_handler(rows, afd_logic)
