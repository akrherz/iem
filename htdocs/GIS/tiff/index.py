"""
Create a wall of links for generation of GeoTIFFs
"""
import os
import subprocess
import tempfile
from calendar import month_abbr
from datetime import datetime

from paste.request import parse_formvars
from pyiem.htmlgen import make_select
from pyiem.templates.iem import TEMPLATE
from pyiem.util import utc

HEADER = """
<ol class="breadcrumb">
 <li><a href="/GIS/">GIS Homepage</a></li>
 <li class="active">Download TIFFs</li>
</ol>

<h3>Grib to TIFF Server:</h3>

<p>The IEM archives a lot of grib imagery, this service presents it for a
given UTC date with links to download what is available.</p>

<form name="ds">
%(ys)s &nbsp; %(ms)s &nbsp; %(ds)s &nbsp;
<input type="submit" value="Select Date">
</form>
"""
SOURCES = {
    "5kmffg": {
        "re": "5kmffg_%Y%m%d%H.grib2",
    },
}


def generate_ui(valid, res):
    """Make the UI for the given date."""
    # FFG
    for hr in range(0, 24, 6):
        tstr = f"{valid:%Y%m%d}{hr:02.0f}"
        testfn = (
            f"/mesonet/ARCHIVE/data/{valid:%Y/%m/%d}/model/ffg/5kmffg_"
            f"{tstr}.grib2"
        )
        if not os.path.isfile(testfn):
            continue
        href = f"/GIS/tiff/?service=5kmffg&amp;ts={tstr}"
        grbfn = testfn.rsplit("/", 1)[-1]
        href2 = testfn.replace("/mesonet/ARCHIVE/", "/archive/")
        res["content"] += (
            f'<br />{grbfn} <a href="{href}">As GeoTIFF</a>, '
            f'<a href="{href2}">As Grib</a>'
        )


def workflow(tmpdir, ts):
    """Go ts."""
    valid = datetime.strptime(ts, "%Y%m%d%H")
    testfn = (
        f"/mesonet/ARCHIVE/data/{valid:%Y/%m/%d}/model/ffg/5kmffg_"
        f"{valid:%Y%m%d%H}.grib2"
    )
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


def application(environ, start_response):
    """mod-wsgi handler."""
    fdict = parse_formvars(environ)
    service = fdict.get("service")
    if service in SOURCES:
        ts = fdict.get("ts")
        headers = [
            ("Content-type", "application/octet-stream"),
            (
                "Content-Disposition",
                f"attachment; filename={service}_{ts}.tiff",
            ),
        ]
        start_response("200 OK", headers)
        with tempfile.TemporaryDirectory() as tmpdir:
            return [workflow(tmpdir, fdict.get("ts"))]

    valid = utc(
        int(fdict.get("year", utc().year)),
        int(fdict.get("month", utc().month)),
        int(fdict.get("day", utc().day)),
    )

    headers = [("Content-type", "text/html")]
    res = {
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
        }
    }
    generate_ui(valid, res)

    start_response("200 OK", headers)
    return [TEMPLATE.render(res).encode("utf-8")]
