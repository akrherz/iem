""".. title:: VTEC Browser

This is the front end for the IEM VTEC browser.  The implementation of the
app is found at `Github iemvtec repo <https://github.com/akrherz/iemvtec>`_.

"""

import json
import os
import re

from pydantic import Field, field_validator
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE
from pyiem.templates.iem import TEMPLATE
from pyiem.util import html_escape, utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection

from iemweb.mlib import rectify_wfo
from iemweb.util import error_log

# sadly, I have a lot of links in the wild without a status?
VTEC_FORM = (
    r"(?P<year>\d+)-(?P<op>O)-(?P<status>[A-Z]{3})?-?(?P<wfo4>[A-Z]{4})-"
    r"(?P<phenomena>[A-Z]{2})-(?P<significance>[A-Z])-(?P<eventid>\d+)"
)
VTEC_RE = re.compile(f"^{VTEC_FORM}$")
LEGACY_URL_RE = re.compile(f"/event/{VTEC_FORM}")


class Schema(CGIModel):
    """See how we are called."""

    vtec: str = Field(None, description="VTEC String", pattern=VTEC_RE)
    wfo: str = Field(
        "DMX",
        description="WFO Identifier",
        pattern=r"^[A-Z]{3,4}$",
        max_length=4,
    )
    eventid: int = Field(
        45,
        description="Event Identifier",
        ge=1,
        le=9999,
    )
    phenomena: str = Field(
        "TO",
        description="VTEC Phenomena",
        pattern=r"^[A-Z]{2}$",
        max_length=2,
    )
    significance: str = Field(
        "W",
        description="VTEC Significance",
        pattern=r"^[A-Z]$",
        max_length=1,
    )
    year: int = Field(
        2024,
        description="VTEC Year",
        ge=1980,  # first year of VTEC
        le=utc().year + 1,  # allow next year
    )

    @field_validator("wfo", mode="before")
    @classmethod
    def rectify_wfo(cls, value: str) -> str:
        """Ensure WFO is 4 characters."""
        return rectify_wfo(value)


@with_sqlalchemy_conn("postgis")
def get_data(vtecinfo: dict, conn: Connection | None = None):
    """Get aux data from the database about this event."""
    res = conn.execute(
        sql_helper(
            "SELECT max(product_ids[cardinality(product_ids)]) as r, "
            "sumtxt(name::text || ', ') as cnties, "
            "max(case when is_emergency then 1 else 0 end), "
            "max(case when is_pds then 1 else 0 end), "
            "max(updated at time zone 'UTC') from "
            "warnings w JOIN ugcs u on (w.gid = u.gid) WHERE vtec_year = :yr "
            "and w.wfo = :wfo and phenomena = :ph and significance = :sig "
            "and eventid = :eventid"
        ),
        {
            "yr": vtecinfo["year"],
            "wfo": vtecinfo["wfo"][-3:],
            "ph": vtecinfo["phenomena"],
            "sig": vtecinfo["significance"],
            "eventid": int(vtecinfo["eventid"]),
        },
    )
    row = res.fetchone()
    vtecinfo["report"] = (
        "" if row[0] is None else html_escape(row[0].replace("\001", ""))
    )
    vtecinfo["desc"] = "" if row[1] is None else html_escape(row[1][:-2])
    vtecinfo["is_emergency"] = row[2] == 1
    vtecinfo["is_pds"] = row[3] == 1
    vtecinfo["updated"] = utc() if row[4] is None else row[4]


def as_html(vtecinfo: dict):
    """Generate the HTML page."""
    vtecinfo["ogtitle"] = "%s %s%s %s #%s" % (
        vtecinfo["wfo"],
        VTEC_PHENOMENA.get(vtecinfo["phenomena"]),
        " (Particularly Dangerous Situation) " if vtecinfo["is_pds"] else "",
        (
            "Emergency"
            if vtecinfo["is_emergency"]
            else VTEC_SIGNIFICANCE.get(vtecinfo["significance"])
        ),
        int(vtecinfo["eventid"]),
    )
    vtecinfo["ogimg"] = (
        "https://mesonet.agron.iastate.edu/plotting/auto/plot/208/"
        "network:WFO::wfo:%s::year:%s::phenomenav:%s::significancev:%s::"
        "etn:%s"
    ) % (
        (
            vtecinfo["wfo"]
            if vtecinfo["wfo"].startswith("P")
            else vtecinfo["wfo"][-3:]
        ),
        vtecinfo["year"],
        vtecinfo["phenomena"],
        vtecinfo["significance"],
        vtecinfo["eventid"],
    )
    vtecinfo["ogurl"] = (
        f"https://mesonet.agron.iastate.edu/vtec/?wfo={vtecinfo['wfo']}&amp;"
        f"phenomena={vtecinfo['phenomena']}&amp;"
        f"significance={vtecinfo['significance']}&amp;"
        f"eventid={vtecinfo['eventid']}&amp;year={vtecinfo['year']}"
    )


def get_context(environ: dict) -> dict:
    """Figure out how we were called."""
    ctx = {
        "appmode": True,  # causes no inclusion of default CSS/JS
        "title": "NWS Valid Time Event Code (VTEC) Browser",
        "headextra": "",
        "jsextra": "",
    }
    assetfn = "/opt/iem/htdocs/vtec/assets.json"
    if os.path.isfile(assetfn):
        try:
            with open(assetfn) as fh:
                assets = json.load(fh)["content.js"]
            ctx["headextra"] = f"""
<link rel="stylesheet" href="/vtec/{assets["css"][0]}">
"""
            ctx["jsextra"] = f"""
<script src="/vtec/{assets["file"]}" type="module"></script>
"""
        except Exception as exp:
            error_log(environ, f"Failed to load assets.json: {exp}")

    get_data(environ)
    as_html(environ)
    ctx["title"] = environ["ogtitle"]
    ctx["headextra"] += f"""
<meta property="og:title" content="{environ["ogtitle"]}">
<meta property="og:description" content="{environ["desc"]}">
<meta property="og:image" content="{environ["ogimg"]}.png">
<meta property="og:url" content="{environ["ogurl"]}">
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
    script_uri = environ.get("SCRIPT_URI", "")
    m = LEGACY_URL_RE.search(script_uri)
    if m:
        # Pivot to use URL Parameters
        urlparams = {}
        tokens = script_uri.split("/")
        for i, token in enumerate(tokens[:-1]):  # chomp last to prevent err
            if token not in ["event", "tab", "update", "radar"]:
                continue
            value = tokens[i + 1]
            if token == "event":
                m = VTEC_RE.match(value)
                if m is not None:
                    vtec = m.groupdict()
                    urlparams["wfo"] = vtec["wfo4"]
                    urlparams["phenomena"] = vtec["phenomena"]
                    urlparams["significance"] = vtec["significance"]
                    urlparams["eventid"] = vtec["eventid"]
                    urlparams["year"] = vtec["year"]
            if token in ["tab", "update"]:
                urlparams[token] = value
            if token == "radar":
                radtokens = value.split("-")
                if len(radtokens) == 3:
                    urlparams["radar"] = radtokens[0]
                    urlparams["radar_product"] = radtokens[1]
                    urlparams["radar_time"] = radtokens[2]

        # Forward the request to the new URL
        url = "/vtec/?" + "&".join(
            f"{k}={v}" for k, v in urlparams.items() if v is not None
        )
        start_response("301 Moved Permanently", [("Location", url)])
        return [b"Redirecting"]

    # If vtec cgi param, redirect to /vtec/event/...
    if environ["vtec"] is not None:
        url = f"/vtec/event/{environ['vtec']}"
        start_response("301 Moved Permanently", [("Location", url)])
        return [b"Redirecting"]
    ctx = get_context(environ)
    start_response("200 OK", [("Content-type", "text/html")])
    return TEMPLATE.render(ctx).encode("utf-8")
