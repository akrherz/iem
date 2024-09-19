"""Write NEXRAD composite sector views to archive.

run from RUN_5MIN.sh
"""

import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

import click
import httpx
from pyiem.database import get_dbconnc
from pyiem.util import archive_fetch, exponential_backoff, logger, utc

LOG = logger()
N0QBASE = utc(2010, 11, 14)
IEM = "http://mesonet.agron.iastate.edu"


def save(sectorName, file_name, dir_name, ts, routes, bbox=None):
    """Get an image and write it back to LDM for archiving"""
    tstamp = ts.strftime("%Y%m%d%H%M")
    nexrad = "nexrad" if ts < N0QBASE else "n0q"
    layers = (
        f"layers[]={nexrad}&layers[]=watch_by_county&layers[]=sbw&"
        "layers[]=uscounties"
    )
    if sectorName == "conus":
        layers = f"layers[]={nexrad}&layers[]=watch_by_county"
    uri = f"{IEM}/GIS/radmap.php?sector={sectorName}&ts={tstamp}&{layers}"
    if bbox is not None:
        uri = f"{IEM}/GIS/radmap.php?bbox={bbox}&ts={tstamp}&{layers}"
    req = exponential_backoff(httpx.get, uri, timeout=60)
    if req is None or req.status_code != 200:
        LOG.warning("%s failure", uri)
        return

    with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
        tmpfd.write(req.content)

    cmd = [
        "pqinsert",
        "-p",
        f"plot {routes} {tstamp} {file_name} "
        f"{dir_name}/n0r_{tstamp[:8]}_{tstamp[8:]}.png png",
        tmpfd.name,
    ]
    subprocess.call(cmd)
    os.unlink(tmpfd.name)


def runtime(ts: datetime, routes: str):
    """Actually run for a time"""
    pgconn, pcursor = get_dbconnc("postgis")

    save("conus", "uscomp.png", "usrad", ts, routes)
    save("iem", "mwcomp.png", "comprad", ts, routes)
    for i in ["lot", "ict", "sd", "hun"]:
        save(i, f"{i}comp.png", f"{i}rad", ts, routes)

    # SEL starts in about 2007
    if ts.year < 2007:
        return

    # Now, we query for watches.
    pcursor.execute(
        """
        with data as (
            select sel, rank() OVER (PARTITION by sel ORDER by issued DESC),
            ST_xmax(geom), ST_xmin(geom), ST_ymax(geom), ST_ymin(geom)
            from watches where issued < %s and issued > %s)
        select trim(sel) as ss, st_xmax, st_xmin, st_ymax, st_ymin from data
        where rank = 1
        """,
        (ts, ts - timedelta(days=120)),
    )
    for row in pcursor:
        xmin = float(row["st_xmin"]) - 0.75
        ymin = float(row["st_ymin"]) - 0.75
        xmax = float(row["st_xmax"]) + 0.75
        ymax = float(row["st_ymax"]) + 1.5
        bbox = f"{xmin},{ymin},{xmax},{ymax}"
        sel = row["ss"].lower()
        save("custom", f"{sel}comp.png", f"{sel}rad", ts, routes, bbox)
    pgconn.close()


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
def main(valid: datetime):
    """Go Main Go"""
    valid = valid.replace(tzinfo=timezone.utc)
    LOG.info("Running for %s", valid)
    # If we are near real-time, also check various archive points
    if (utc() - valid).total_seconds() > 1000:
        runtime(valid, "a")
        return
    runtime(valid, "ac")
    for hroff in [1, 3, 7, 12, 24]:
        valid = valid - timedelta(hours=hroff)
        ppath = (
            f"{valid:%Y}/{valid:%m}/{valid:%d}/"
            f"comprad/n0r_{valid:%Y%m%d}_{valid:%H%M}.png"
        )
        with archive_fetch(ppath) as fh:
            if fh is None:
                LOG.warning("Missing %s", ppath)
                runtime(valid, "a")


if __name__ == "__main__":
    main()
