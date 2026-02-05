"""Frontend for Feature Content, such that we can make some magic happen"""

import os
import re
from datetime import date
from io import BytesIO

from matplotlib.figure import Figure
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import iemapp
from sqlalchemy.engine import Connection

PATTERN = re.compile(
    "^/onsite/features/(?P<yyyy>[0-9]{4})/(?P<mm>[0-9]{2})/"
    "(?P<yymmdd>[0-9]{6})(?P<extra>.*)."
    "(?P<suffix>png|gif|jpg|xls|pdf|gnumeric|mp4)$"
)


@with_sqlalchemy_conn("mesosite")
def dblog(yymmdd: str, conn: Connection | None = None):
    """Log this request"""
    dt = date(2000 + int(yymmdd[:2]), int(yymmdd[2:4]), int(yymmdd[4:6]))
    conn.execute(
        sql_helper(
            "UPDATE feature SET views = views + 1 WHERE date(valid) = :dt"
        ),
        {"dt": dt},
    )
    conn.commit()


def get_content_type(val):
    """return the content-type header entry."""
    if val == "text":
        ct = "text/plain"
    elif val in ["png", "gif", "jpg"]:
        ct = f"image/{val}"
    elif val == "mp4":
        ct = f"video/{val}"
    elif val == "pdf":
        ct = f"application/{val}"
    else:
        ct = "text/plain"
    return ("Content-type", ct)


@iemapp()
def application(environ, start_response):
    """Process this request

    This should look something like "/onsite/features/2016/11/161125.png"
    """
    headers = [("Accept-Ranges", "bytes")]
    uri = environ.get("REQUEST_URI")
    # Option 1, no URI is provided.
    if uri is None:
        raise IncompleteWebRequest("Missing parameters in request")
    match = PATTERN.match(uri)
    # Option 2, the URI pattern is unknown.
    if match is None:
        raise IncompleteWebRequest("Missing parameters in request")

    data = match.groupdict()
    fn = (
        "/mesonet/share/features/%(yyyy)s/%(mm)s/"
        "%(yymmdd)s%(extra)s.%(suffix)s"
    ) % data
    # Option 3, we have no file.
    if not os.path.isfile(fn):
        headers.append(get_content_type("png"))
        fig = Figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.text(
            0.5,
            0.5,
            "Feature Image was not Found!",
            transform=ax.transAxes,
            ha="center",
        )
        ax.axis("off")
        ram = BytesIO()
        fig.savefig(ram, format="png")
        ram.seek(0)
        start_response("404 Not Found", headers)
        return [ram.read()]

    # Option 4, we can support this request.
    headers.append(get_content_type(data["suffix"]))
    rng = environ.get("HTTP_RANGE", "bytes=0-")
    tokens = rng.replace("bytes=", "").split("-", 1)
    with open(fn, "rb") as fh:
        resdata = fh.read()
    totalsize = len(resdata)
    stripe = slice(
        int(tokens[0]),
        totalsize if tokens[-1] == "" else (int(tokens[-1]) + 1),
    )
    status = "200 OK"
    if totalsize != (stripe.stop - stripe.start):
        status = "206 Partial Content"
    headers.append(("Content-Length", "%.0f" % (stripe.stop - stripe.start,)))
    if environ.get("HTTP_RANGE") and stripe is not None:
        secondval = (
            ""
            if environ.get("HTTP_RANGE") == "bytes=0-"
            else (stripe.stop - 1)
        )
        headers.append(
            (
                "Content-Range",
                f"bytes {stripe.start}-{secondval}/{totalsize}",
            )
        )
    try:
        dblog(data["yymmdd"])
    finally:
        # Swallow exception
        start_response(status, headers)
    return [resdata[stripe]]
