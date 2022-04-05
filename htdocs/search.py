"""Answer search requests, oh boy."""
# Local
import re

# Third Party
from commonregex import CommonRegex
import pandas as pd
from pyiem.templates.iem import TEMPLATE
from pyiem.util import get_sqlalchemy_conn, get_properties
from paste.request import parse_formvars
import requests

STATION_RE = re.compile(r"^[A-Z0-9]{3,10}$", re.I)
AUTOPLOT_RE = re.compile(r"^(autoplot|ap)?\s?(?P<n>\d{1,3})$", re.I)


def station_df_handler(df):
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
    props = get_properties()
    req = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params=dict(address=q, key=props["google.maps.key2"], sensor="true"),
    )
    data = req.json()
    if not data["results"]:
        return "/sites/locate.php"
    lat = data["results"][0]["geometry"]["location"]["lat"]
    lon = data["results"][0]["geometry"]["location"]["lng"]
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            "SELECT id, network, "
            "ST_Distance(geom, "
            "ST_GeomFromEWKT('SRID=4326;POINT(%s %s)')) as dist "
            "from stations where ST_PointInsideCircle(geom, %s, %s, 1) "
            "ORDER by dist ASC LIMIT 50",
            conn,
            params=(lon, lat, lon, lat),
        )
    return station_df_handler(df)


def ap_handler(apid):
    """Forward to the appropriate autoplot page."""
    return f"/plotting/auto/?q={apid}"


def station_handler(sid):
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


def find_handler(q):
    """Do we have a handler for this request?"""
    if q == "":
        return None, None
    # Match autoplot first as ### will match STATION_RE
    m = AUTOPLOT_RE.match(q)
    if m:
        d = m.groupdict()
        return ap_handler, d["n"]
    if STATION_RE.match(q):
        return station_handler, q.upper()
    # Likely want to always do this one last, as it will catch things
    c = CommonRegex(q)
    # pylint: disable=no-member
    if c.street_addresses:
        return geocoder, q
    return None, None


def default_form():
    """Page when we don't know what to do."""
    ctx = {}
    ctx[
        "content"
    ] = """
<h3>IEM Awesome Search Failure</h3>

<p>Sorry, I don't know how to handle your request. Here's a brief listing
of supported search values.</p>

<ul>
    <li>A station ID (KFWS, AMSI4, DSM, IA0200)</li>
    <li>An autoplot identifier (ap1, ap2, autoplot 100)</li>
    <li>The nearest station to a street address (123 Main St Ames Iowa)</li>
</ul>

<p>Wanna see something added? <a href="/info/contacts.php">Contact us</a>!</p>
    """
    return [TEMPLATE.render(ctx).encode("utf-8")]


def application(environ, start_response):
    """Here we are, answer with a redirect in most cases."""
    form = parse_formvars(environ)
    q = form.get("q", "").strip()
    handler, qclean = find_handler(q)
    if handler is None:
        start_response("200 OK", [("Content-type", "text/html")])
        return default_form()
    redirect_to = handler(qclean)
    start_response("302 Found", [("Location", redirect_to)])
    return []
