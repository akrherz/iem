"""Generate a web crawler friendly page."""
import re

from pyiem.util import get_dbconn, html_escape, utc
from pyiem.nws import vtec

# sadly, I have a lot of links in the wild without a status?
VTEC_RE = re.compile(
    r"^(?P<year>\d+)-(?P<op>O)-(?P<status>[A-Z]{3})?-?(?P<wfo4>[A-Z]{4})-"
    r"(?P<phenomena>[A-Z]{2})-(?P<significance>[A-Z])-(?P<eventid>\d+)$"
)
TIME_RE = re.compile(
    r"(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)T(?P<hour>\d+):(?P<minute>\d+)"
)


def get_data(ctx):
    """Get aux data from the database about this event."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    table = "warnings_%s" % (ctx["year"],)
    cursor.execute(
        (
            "SELECT max(report) as r, sumtxt(name::text || ', ') as cnties, "
            "max(case when is_emergency then 1 else 0 end), "
            "max(case when is_pds then 1 else 0 end), "
            "max(updated at time zone 'UTC') from "
            f"{table} w JOIN ugcs u on (w.gid = u.gid) WHERE "
            "w.wfo = %s and phenomena = %s and significance = %s "
            "and eventid = %s"
        ),
        (
            ctx["wfo4"][-3:],
            ctx["phenomena"],
            ctx["significance"],
            int(ctx["eventid"]),
        ),
    )
    row = cursor.fetchone()
    ctx["report"] = (
        "" if row[0] is None else html_escape(row[0].replace("\001", ""))
    )
    ctx["desc"] = "" if row[1] is None else html_escape(row[1][:-2])
    ctx["is_emergency"] = row[2] == 1
    ctx["is_pds"] = row[3] == 1
    ctx["updated"] = utc() if row[4] is None else row[4]


def as_html(ctx):
    """Generate the HTML page."""
    ctx["v"] = (
        "%(year)s-%(op)s-%(status)s-%(wfo4)s-%(phenomena)s-"
        "%(significance)s-%(eventid)s"
    ) % ctx
    ctx["ogtitle"] = "%s %s%s %s #%s" % (
        ctx["wfo4"],
        vtec.VTEC_PHENOMENA.get(ctx["phenomena"]),
        " (Particularly Dangerous Situation) " if ctx["is_pds"] else "",
        (
            "Emergency"
            if ctx["is_emergency"]
            else vtec.VTEC_SIGNIFICANCE.get(ctx["significance"])
        ),
        int(ctx["eventid"]),
    )
    ctx["ogurl"] = ("https://mesonet.agron.iastate.edu/vtec/f/%s") % (
        ctx["v"],
    )
    ctx["ogimg"] = (
        "https://mesonet.agron.iastate.edu/plotting/auto/plot/208/"
        "network:WFO::wfo:%s::year:%s::phenomenav:%s::significancev:%s::"
        "etn:%s"
    ) % (
        ctx["wfo4"] if ctx["wfo4"].startswith("P") else ctx["wfo4"][-3:],
        ctx["year"],
        ctx["phenomena"],
        ctx["significance"],
        ctx["eventid"],
    )
    if ctx["valid"] is not None:
        ctx["ogurl"] += "_" + ctx["valid"].strftime("%Y-%m-%dT%H:%MZ")
        ctx["ogimg"] += "::valid:%s::_updated:%s" % (
            ctx["valid"].strftime("%Y-%m-%d%%20%H%M"),
            ctx["updated"].strftime("%Y-%m-%d%%20%H%M"),
        )
    return (
        """
<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="refresh" content="0; URL=/vtec/#%(v)s">
<title>%(ogtitle)s</title>
<meta property="og:title" content="%(ogtitle)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:image" content="%(ogimg)s.png">
<meta property="og:url" content="%(ogurl)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@akrherz">
<meta name="og:image:width" content="1200">
<meta name="og:image:height" content="628">
<meta name="og:site_name" content="Iowa Environmental Mesonet">
<meta name="twitter:image:alt" content="Visualization of the VTEC Product">
</head>
<body>
<pre>
%(report)s
</pre>

</body>
</html>
"""
        % ctx
    )


def get_context(url):
    """Figure out how we were called."""
    # /vtec/f/2020-O-NEW-KLWX-SC-Y-0026
    # /vtec/f/2020-O-NEW-KLWX-SC-Y-0026_2020-02-18T17:00Z
    tokens = url.split("/")[-1].split("_")
    m = VTEC_RE.match(tokens[0])
    if m is None:
        return {}
    ctx = m.groupdict()
    if ctx["status"] is None:
        ctx["status"] = "NEW"
    get_data(ctx)
    ctx["valid"] = None
    if len(tokens) > 1:
        m = TIME_RE.match(tokens[1])
        if m:
            d = m.groupdict()
            ctx["valid"] = utc(
                int(d["year"]),
                int(d["month"]),
                int(d["day"]),
                int(d["hour"]),
                int(d["minute"]),
            )
    return ctx


def application(environ, start_response):
    """Answer the bell."""
    ctx = get_context(environ["SCRIPT_URL"])
    if not ctx:
        start_response("404 Not Found", [("Content-type", "text/plain")])
        return [b"Resource Not Found"]
    start_response("200 OK", [("Content-type", "text/html")])
    return [as_html(ctx).encode("ascii", errors="ignore")]
