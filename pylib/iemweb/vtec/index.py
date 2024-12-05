"""..title:: VTEC Browser

TBW.

"""

import re

from pydantic import Field
from pyiem.database import get_dbconn
from pyiem.nws import vtec
from pyiem.templates.iem import TEMPLATE
from pyiem.util import html_escape, utc
from pyiem.webutil import CGIModel, iemapp

# sadly, I have a lot of links in the wild without a status?
VTEC_FORM = (
    r"(?P<year>\d+)-(?P<op>O)-(?P<status>[A-Z]{3})?-?(?P<wfo4>[A-Z]{4})-"
    r"(?P<phenomena>[A-Z]{2})-(?P<significance>[A-Z])-(?P<eventid>\d+)"
)
VTEC_RE = re.compile(f"^{VTEC_FORM}$")
VTEC_IN_URL_RE = re.compile(f"/event/{VTEC_FORM}")


class Schema(CGIModel):
    """See how we are called."""

    vtec: str = Field(None, description="VTEC String", pattern=VTEC_RE)


def get_data(vtecinfo: dict):
    """Get aux data from the database about this event."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        (
            "SELECT max(product_ids[cardinality(product_ids)]) as r, "
            "sumtxt(name::text || ', ') as cnties, "
            "max(case when is_emergency then 1 else 0 end), "
            "max(case when is_pds then 1 else 0 end), "
            "max(updated at time zone 'UTC') from "
            "warnings w JOIN ugcs u on (w.gid = u.gid) WHERE vtec_year = %s "
            "and w.wfo = %s and phenomena = %s and significance = %s "
            "and eventid = %s"
        ),
        (
            vtecinfo["year"],
            vtecinfo["wfo4"][-3:],
            vtecinfo["phenomena"],
            vtecinfo["significance"],
            int(vtecinfo["eventid"]),
        ),
    )
    row = cursor.fetchone()
    vtecinfo["report"] = (
        "" if row[0] is None else html_escape(row[0].replace("\001", ""))
    )
    vtecinfo["desc"] = "" if row[1] is None else html_escape(row[1][:-2])
    vtecinfo["is_emergency"] = row[2] == 1
    vtecinfo["is_pds"] = row[3] == 1
    vtecinfo["updated"] = utc() if row[4] is None else row[4]
    cursor.close()
    pgconn.close()


def as_html(vtecinfo: dict):
    """Generate the HTML page."""
    vtecinfo["v"] = (
        "%(year)s-%(op)s-%(status)s-%(wfo4)s-%(phenomena)s-"
        "%(significance)s-%(eventid)s"
    ) % vtecinfo
    vtecinfo["ogtitle"] = "%s %s%s %s #%s" % (
        vtecinfo["wfo4"],
        vtec.VTEC_PHENOMENA.get(vtecinfo["phenomena"]),
        " (Particularly Dangerous Situation) " if vtecinfo["is_pds"] else "",
        (
            "Emergency"
            if vtecinfo["is_emergency"]
            else vtec.VTEC_SIGNIFICANCE.get(vtecinfo["significance"])
        ),
        int(vtecinfo["eventid"]),
    )
    vtecinfo["ogurl"] = (
        f"https://mesonet.agron.iastate.edu/vtec/event/{vtecinfo['v']}"
    )
    vtecinfo["ogimg"] = (
        "https://mesonet.agron.iastate.edu/plotting/auto/plot/208/"
        "network:WFO::wfo:%s::year:%s::phenomenav:%s::significancev:%s::"
        "etn:%s"
    ) % (
        (
            vtecinfo["wfo4"]
            if vtecinfo["wfo4"].startswith("P")
            else vtecinfo["wfo4"][-3:]
        ),
        vtecinfo["year"],
        vtecinfo["phenomena"],
        vtecinfo["significance"],
        vtecinfo["eventid"],
    )


def get_context(script_url: str) -> dict:
    """Figure out how we were called."""
    ctx = {
        "title": "NWS Valid Time Event Code (VTEC) Browser",
        "headextra": """
<link rel="stylesheet"
 href="/vendor/jquery-datatables/1.10.20/datatables.min.css" />
<link rel="stylesheet"
 href="/vendor/jquery-ui/1.13.2/jquery-ui.min.css" />
<link rel='stylesheet' href="/vendor/openlayers/10.1.0/ol.css" type='text/css'>
<link type="text/css" href="/vendor/openlayers/10.1.0/ol-layerswitcher.css"
 rel="stylesheet" />
<link rel="stylesheet" href="/vtec/vtec_static.css" />
""",
        "jsextra": """
<script src="/vendor/jquery-datatables/1.10.20/datatables.min.js"></script>
<script src="/vendor/jquery-ui/1.13.2/jquery-ui.js"></script>
<script src="/vendor/moment/2.13.0/moment.min.js"></script>
<script src='/vendor/openlayers/10.1.0/ol.js'></script>
<script src='/vendor/openlayers/10.1.0/ol-layerswitcher.js'></script>
<script type="text/javascript" src="/vtec/vtec_static.js?20241205"></script>
<script type="text/javascript" src="/vtec/vtec_app.js?20241113"></script>
""",
    }
    # /vtec/event/2019-O-NEW-KDMX-SV-W-0001
    m = VTEC_IN_URL_RE.search(script_url)

    if m:
        vtecinfo = m.groupdict()
        get_data(vtecinfo)
        as_html(vtecinfo)
        ctx["title"] = vtecinfo["ogtitle"]
        ctx["headextra"] += f"""
<meta property="og:title" content="{vtecinfo['ogtitle']}">
<meta property="og:description" content="{vtecinfo['desc']}">
<meta property="og:image" content="{vtecinfo['ogimg']}.png">
<meta property="og:url" content="{vtecinfo['ogurl']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@akrherz">
<meta name="og:image:width" content="1200">
<meta name="og:image:height" content="628">
<meta name="og:site_name" content="Iowa Environmental Mesonet">
<meta name="twitter:image:alt" content="Visualization of the VTEC Product">
"""

    with open("/opt/iem/htdocs/vtec/_index_content.html") as fh:
        content = fh.read()
        ctx["content"] = content
    return ctx


@iemapp(schema=Schema, help=__doc__)
def application(environ, start_response):
    """Answer the bell."""
    # Force HTTPS as the openlayers map will be angry
    if environ["wsgi.url_scheme"] != "https":
        url = f"https://{environ['HTTP_HOST']}{environ['REQUEST_URI']}"
        start_response("301 Moved Permanently", [("Location", url)])
        return [b"Redirecting"]
    # If vtec cgi param, redirect to /vtec/event/...
    if environ["vtec"] is not None:
        url = f"/vtec/event/{environ['vtec']}"
        start_response("301 Moved Permanently", [("Location", url)])
        return [b"Redirecting"]
    ctx = get_context(environ.get("SCRIPT_URI", ""))
    start_response("200 OK", [("Content-type", "text/html")])
    return TEMPLATE.render(ctx).encode("utf-8")
