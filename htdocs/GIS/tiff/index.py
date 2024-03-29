"""
Create a wall of links for generation of GeoTIFFs
"""

import os
import subprocess
import tempfile
from calendar import month_abbr
from datetime import datetime, timedelta

from pyiem.exceptions import IncompleteWebRequest
from pyiem.htmlgen import make_select
from pyiem.templates.iem import TEMPLATE
from pyiem.util import utc
from pyiem.webutil import iemapp

HEADER = """
<ol class="breadcrumb">
 <li><a href="/GIS/">GIS Homepage</a></li>
 <li class="active">Download TIFFs</li>
</ol>

<h3>Grib to TIFF Service:</h3>

<p>The IEM archives a lot of grib imagery, this service presents it for a
given UTC date with links to download what is available.</p>

<form name="ds">
%(ys)s &nbsp; %(ms)s &nbsp; %(ds)s &nbsp;
<input type="submit" value="Select Date">
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


def generate_ui(key, valid, res):
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
        testfn = f"/mesonet/ARCHIVE/data/{ts.strftime(meta['re'])}"
        if not os.path.isfile(testfn):
            continue
        found = True
        href = f"/GIS/tiff/?service={key}&amp;ts={ts:%Y%m%d%H%M}"
        grbfn = testfn.rsplit("/", 1)[-1]
        href2 = testfn.replace("/mesonet/ARCHIVE/", "/archive/")
        res["content"] += (
            f'<br />{grbfn} <a href="{href}">As GeoTIFF</a>, '
            f'<a href="{href2}">As Grib</a>'
        )
    if not found:
        res["content"] += "<p>Failed to find any archived files.</p>"


def workflow(key, tmpdir, ts):
    """Go ts."""
    meta = SOURCES[key]
    if ts is None:
        # Go to 0z tomorrow and work backwards
        valid = (utc() + timedelta(days=1)).replace(hour=0, minute=0)
        found = False
        for offset in range(0, 25, meta["modulo"]):
            ts = valid - timedelta(hours=offset)
            testfn = f"/mesonet/ARCHIVE/data/{ts.strftime(meta['re'])}"
            if os.path.isfile(testfn):
                found = True
                break
        if not found:
            raise FileNotFoundError("Failed to find recent file for service")

    else:
        try:
            valid = datetime.strptime(ts, "%Y%m%d%H%M")
        except Exception as exp:
            raise IncompleteWebRequest("Invalid ts provided") from exp
        testfn = (
            f"/mesonet/ARCHIVE/data/{valid:%Y/%m/%d}/model/ffg/5kmffg_"
            f"{valid:%Y%m%d%H}.grib2"
        )
        if not os.path.isfile(testfn):
            raise FileNotFoundError("Failed to find file for service.")
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
    with open(f"{tmpdir}/test.tiff", "rb") as fh:
        return fh.read()


@iemapp()
def application(environ, start_response):
    """mod-wsgi handler."""
    service = environ.get("service")
    if service in SOURCES:
        ts = environ.get("ts", "current")[:12]
        headers = [
            ("Content-type", "application/octet-stream"),
            (
                "Content-Disposition",
                f"attachment; filename={service}_{ts}.tiff",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                res = workflow(service, tmpdir, environ.get("ts"))
                start_response("200 OK", headers)
                return [res]
            except FileNotFoundError:
                start_response(
                    "400 Bad Request", [("Content-type", "text/plain")]
                )
                return [b"File not found for service/ts combination."]

    valid = utc(
        int(environ.get("year", utc().year)),
        int(environ.get("month", utc().month)),
        int(environ.get("day", utc().day)),
    )

    headers = [("Content-type", "text/html")]
    res = {
        "IEM_APPID": 33,
        "content": HEADER
        % {
            "ys": make_select(
                "year",
                valid.year,
                dict(zip(range(2000, 2024), range(2000, 2024))),
                showvalue=False,
            ),
            "ms": make_select(
                "month",
                valid.month,
                dict(zip(range(1, 13), month_abbr[1:])),
                showvalue=False,
            ),
            "ds": make_select(
                "day",
                valid.day,
                dict(zip(range(1, 32), range(1, 32))),
                showvalue=False,
            ),
        },
    }
    for key in SOURCES:
        generate_ui(key, valid, res)

    start_response("200 OK", headers)
    return [TEMPLATE.render(res).encode("utf-8")]
