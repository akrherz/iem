""".. title:: Create wall of links to the TIFF service

Usage Examples
--------------

Provide a list of links for 9 Sep 2025 UTC

https://mesonet.agron.iastate.edu/GIS/tiff/index.py?year=2025&month=9&day=9

Get a RTMA grid as a GeoTIFF

https://mesonet.agron.iastate.edu/GIS/tiff/index.py?\
service=rtma&ts=202509090000

"""

import logging
import subprocess
import tempfile
from calendar import month_abbr
from datetime import datetime, timedelta

from pydantic import Field
from pyiem.exceptions import IncompleteWebRequest
from pyiem.htmlgen import make_select
from pyiem.templates.iem import TEMPLATE
from pyiem.util import archive_fetch, utc
from pyiem.webutil import CGIModel, iemapp

LOG = logging.getLogger(__name__)


class MyModel(CGIModel):
    """See how we are called."""

    service: str = Field(
        None,
        title="Service to use",
        description="Service to use",
        pattern="^(5kmffg|rtma)$",
    )
    ts: str = Field(
        None,
        title="Valid UTC Timestamp",
        description="Valid UTC Timestamp in YYYYMMDDHHMM format",
        pattern="^[0-9]{12}$",
    )
    day: int = Field(
        utc().day,
        title="Day",
        description="Day of the month",
        ge=1,
        le=31,
    )
    month: int = Field(
        utc().month,
        title="Month",
        description="Month of the year",
        ge=1,
        le=12,
    )
    year: int = Field(
        utc().year,
        title="Year",
        description="Year",
    )


HEADER = """
<nav aria-label="breadcrumb">
 <ol class="breadcrumb">
  <li class="breadcrumb-item"><a href="/GIS/">GIS Homepage</a></li>
  <li class="breadcrumb-item active" aria-current="page">Download TIFFs</li>
 </ol>
</nav>

<h3>Grib to TIFF Service:</h3>

<p>The IEM archives a lot of grib imagery, this service presents it for a
given UTC date with links to download what is available.</p>

<form name="ds" class="d-inline-flex gap-2 align-items-center">
%(ys)s %(ms)s %(ds)s
<button type="submit" class="btn btn-primary btn-sm">Select Date</button>
</form>
"""
SOURCES = {
    "5kmffg": {
        "label": "Flash Flood Guidance @5km (FFG)",
        "re": "%Y/%m/%d/model/ffg/5kmffg_%Y%m%d%H.grib2",
        "modulo": 6,
    },
    "rtma": {
        "label": "Real-Time Mesoscale Analysis (RTMA)",
        "re": "%Y/%m/%d/model/rtma/%H/rtma.t%Hz.awp2p5f000.grib2",
        "modulo": 1,
    },
}


def generate_ui(key, valid: datetime, res):
    """Make the UI for the given date."""
    meta = SOURCES[key]
    res["content"] += (
        f"<h3>{meta['label']}</h3>"
        f'<p>Real-time stable link: <a href="/GIS/tiff/?service={key}">'
        f"/GIS/tiff/?service={key}</a></p>"
    )
    found = False
    for hr in range(0, 24, meta["modulo"]):
        ts = valid.replace(hour=hr)
        ppath = ts.strftime(meta["re"])
        with archive_fetch(ppath, method="head") as fn:
            if fn is None:
                continue
            found = True
            href = f"/GIS/tiff/?service={key}&amp;ts={ts:%Y%m%d%H%M}"
            res["content"] += (
                f'<br />{ppath} <a href="{href}">As GeoTIFF</a>, '
                f'<a href="/archive/data/{ppath}">As Grib</a>'
            )
    if not found:
        res["content"] += "<p>Failed to find any archived files.</p>"


def workflow(key, tmpdir, ts: datetime | None):
    """Go ts."""
    meta = SOURCES[key]
    if ts is None:
        # Go to 0z tomorrow and work backwards
        valid = (utc() + timedelta(days=1)).replace(hour=0, minute=0)
        found = False
        for offset in range(0, 25, meta["modulo"]):
            ts = valid - timedelta(hours=offset)
            testfn = ts.strftime(meta["re"])
            with archive_fetch(testfn) as testfn:
                if testfn is not None:
                    found = True
                    break
        if not found:
            raise FileNotFoundError("Failed to find recent file for service")

    else:
        try:
            valid = datetime.strptime(ts, "%Y%m%d%H%M")
        except Exception as exp:
            raise IncompleteWebRequest("Invalid ts provided") from exp
        ppath = valid.strftime(meta["re"])
        with archive_fetch(ppath) as testfn:
            if testfn is None:
                raise FileNotFoundError(f"Failed to find {ppath} for service.")
            with subprocess.Popen(
                [
                    "gdalwarp",
                    testfn,
                    f"{tmpdir}/test.tiff",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) as cmd:
                cmd.stdout.read()
    with open(f"{tmpdir}/test.tiff", "rb") as fh:  # skipcq
        return fh.read()


@iemapp(help=__doc__, schema=MyModel)
def application(environ, start_response):
    """mod-wsgi handler."""
    service = environ.get("service")
    if service in SOURCES:
        ts = environ["ts"]
        headers = [
            ("Content-type", "application/octet-stream"),
            (
                "Content-Disposition",
                f"attachment; filename={service}_{ts}.tiff",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                res = workflow(service, tmpdir, ts)
                start_response("200 OK", headers)
                return [res]
            except FileNotFoundError as exp:
                start_response(
                    "400 Bad Request", [("Content-type", "text/plain")]
                )
                return [f"File not found for service/ts combination: {exp}"]

    valid = utc(environ["year"], environ["month"], environ["day"])

    headers = [("Content-type", "text/html")]
    res = {
        "IEM_APPID": 33,
        "content": HEADER
        % {
            "ys": make_select(
                "year",
                valid.year,
                dict(
                    zip(
                        range(2000, utc().year + 1),
                        range(2000, utc().year + 1),
                        strict=True,
                    )
                ),
                showvalue=False,
            ),
            "ms": make_select(
                "month",
                valid.month,
                dict(zip(range(1, 13), month_abbr[1:], strict=True)),
                showvalue=False,
            ),
            "ds": make_select(
                "day",
                valid.day,
                dict(zip(range(1, 32), range(1, 32), strict=False)),
                showvalue=False,
            ),
        },
    }
    for key in SOURCES:
        generate_ui(key, valid, res)

    start_response("200 OK", headers)
    return [TEMPLATE.render(res).encode("utf-8")]
