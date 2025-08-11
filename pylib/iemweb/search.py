""".. title:: IEM Search Service

This service drives the search bar on the IEM website.

Changelog
---------

- 2024-09-04: Initial documentation update

Example Requests
----------------

Search using a station identifier

https://mesonet.agron.iastate.edu/search.py?q=DSM

Search using a four character station identifier

https://mesonet.agron.iastate.edu/search.py?q=KPAH

Provide an IEM AWIPS ID / AFOS identifier

https://mesonet.agron.iastate.edu/search.py?q=202407101919-KDMX-FXUS63-AFDDMX

Search for a given NWS AFOS Product Identifier

https://mesonet.agron.iastate.edu/search.py?q=AAABBB

Link to a given autoplot number

https://mesonet.agron.iastate.edu/search.py?q=ap100

Auto forward to station closest to the given street address

https://mesonet.agron.iastate.edu/search.py?q=100%20Main%20St%20Ames%20Iowa

"""

# Local
import re

import httpx
import pandas as pd

# Third Party
from commonregex import CommonRegex
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.templates.iem import TEMPLATE
from pyiem.webutil import iemapp

AFOS_RE = re.compile(r"^[A-Z0-9]{4,6}$", re.IGNORECASE)
STATION_RE = re.compile(r"^[A-Z0-9\-]{3,32}$", re.IGNORECASE)
AUTOPLOT_RE = re.compile(r"^(autoplot|ap)?\s?(?P<n>\d{1,3})$", re.IGNORECASE)
PRODID_RE = re.compile(r"^[12]\d{11}-[A-Z]{4}-", re.IGNORECASE)


def station_df_handler(df: pd.DataFrame) -> str:
    """Common."""
    if df.empty:
        return "/sites/locate.php"
    # Prioritize network values that contain ASOS
    df2 = df[df["network"].str.contains("ASOS")]
    if not df2.empty:
        r1 = df2.iloc[0]
    else:  # roullete
        r1 = df.iloc[0]
    return f"/sites/site.php?station={r1['id']}&network={r1['network']}"


def geocoder(q):
    """Attempt geocoding."""
    resp = httpx.get(
        "http://iem.local/cgi-bin/geocoder.py",
        params={"address": q},
        timeout=30,
    )
    if resp.status_code != 200:
        return "/sites/locate.php"
    lat, lon = resp.text.split(",")
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            sql_helper("""SELECT id, network,
            ST_Distance(geom, ST_Point(:lon, :lat, 4326)) as dist
            from stations where ST_PointInsideCircle(geom, :lon, :lat, 1)
            ORDER by dist ASC LIMIT 50
            """),
            conn,
            params={"lat": float(lat), "lon": float(lon)},
        )
    return station_df_handler(df)


def ap_handler(apid):
    """Forward to the appropriate autoplot page."""
    return f"/plotting/auto/?q={apid}"


def prodid_handler(pid):
    """Foreward to the product page."""
    return f"/p.php?pid={pid}"


def afos_handler(pil):
    """Forward to AFOS handler."""
    return f"/wx/afos/p.php?pil={pil}"


def station_handler(sid: str) -> str:
    """Attempt to find a station."""
    # convert KXXX to XXX
    if sid.startswith("K") and len(sid) == 4:
        sid = sid[1:]
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            "SELECT id, network from stations where id = %s",
            conn,
            params=(sid,),
        )
    return station_df_handler(df)


def has_station(sid):
    """Le Sigh."""
    # convert KXXX to XXX
    if sid.startswith("K") and len(sid) == 4:
        sid = sid[1:]
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            sql_helper("SELECT id, network from stations where id = :sid"),
            conn,
            params={"sid": sid},
        )
    return not df.empty


def find_handler(q, referer: str | None):
    """Do we have a handler for this request?"""
    if q == "":
        return None, None
    m = PRODID_RE.match(q)
    if m:
        return prodid_handler, q
    # Match autoplot first as ### will match STATION_RE
    m = AUTOPLOT_RE.match(q)
    if m:
        d = m.groupdict()
        return ap_handler, d["n"]
    # Can overlap with AFOS_RE
    if STATION_RE.match(q):
        q = q.upper()
        if has_station(q):
            return station_handler, q.upper()
    if AFOS_RE.match(q):
        return afos_handler, q.upper()
    # Likely want to always do this one last, as it will catch things
    c = CommonRegex(q)
    if c.street_addresses and referer:
        return geocoder, q
    return None, None


def default_form():
    """Page when we don't know what to do."""
    ctx = {}
    ctx["content"] = """
<h3>IEM Awesome Search Failure</h3>

<p>Sorry, I don't know how to handle your request. Here's a brief listing
of supported search values.</p>

<ul>
    <li>A NWS AFOS/AWIPS Idenitifer (AFDDMX, SWODY1)</li>
    <li>A station ID (KFWS, AMSI4, DSM, IA0200)</li>
    <li>An autoplot identifier (ap1, ap2, autoplot 100)</li>
    <li>An IEM Product ID for NWS Prods (201501010000-KDMX-NOUS43-PNSDMX)</li>
    <li>The nearest station to a street address (123 Main St Ames Iowa)</li>
</ul>

<p>Wanna see something added? <a href="/info/contacts.php">Contact us</a>!</p>
    """
    return [TEMPLATE.render(ctx).encode("utf-8")]


@iemapp(help=__doc__)
def application(environ, start_response):
    """Here we are, answer with a redirect in most cases."""
    # Ensure we have only latin-1 characters per URL requirements
    q = (
        environ.get("q", "")
        .strip()
        .encode("latin-1", "replace")
        .decode("utf-8", "replace")
    )
    handler, qclean = find_handler(q, environ.get("HTTP_REFERER"))
    if handler is None:
        start_response("200 OK", [("Content-type", "text/html")])
        return default_form()
    redirect_to = handler(qclean)
    start_response("302 Found", [("Location", redirect_to)])
    return []
