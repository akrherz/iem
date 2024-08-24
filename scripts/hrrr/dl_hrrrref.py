"""Download and archive 1km reflectivity from the NCEP HRRR.

This **replaces** the presently downloaded file.

Run from hrrr_jobs.py
"""

import logging
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from typing import NoReturn, Optional, Union

import click
import httpx
import pygrib
from pyiem.util import archive_fetch, exponential_backoff, logger

AWS = "https://noaa-hrrr-bdp-pds.s3.amazonaws.com/"
LOG = logger()
# HRRR model hours available
HOURS = [18] * 24
for _hr in range(0, 24, 6):
    HOURS[_hr] = 48


def is_archive_complete(valid: datetime) -> Union[Optional[bool], NoReturn]:
    """Ensure we have the right file and is the right size."""
    # 15 minute data out 18 hours (ref + 4 ptype fields)
    answer = 18 * 4 * 5
    # Extended hours, when possible, have hourly data
    answer += (HOURS[valid.hour] - 18) * 5
    # The first timestamp
    answer += 5
    ppath = valid.strftime("%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.refd.grib2")
    with archive_fetch(ppath) as gribfn:
        if gribfn is None:
            return False
        # See how many grib messages we have
        try:
            with pygrib.open(gribfn) as grbs:
                LOG.info(
                    "Found %s messages for %s, want %s",
                    grbs.messages,
                    ppath,
                    answer,
                )
                return grbs.messages == answer
        except Exception as exp:
            logging.debug(exp)
    LOG.warning("Archive file %s is corrupt? Aborting...", ppath)
    sys.exit(1)


def wait_for_upstream(valid: datetime) -> Union[Optional[None], NoReturn]:
    """Wait for upstream availability."""
    lasthour = HOURS[valid.hour]
    if lasthour == 18:
        uri = valid.strftime(
            f"{AWS}hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsubhf{lasthour}.grib2.idx"
        )
    else:
        uri = valid.strftime(
            f"{AWS}hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsfcf{lasthour}.grib2.idx"
        )
    # Wait for at most 45 minutes for the upstream to be available
    for _ in range(45):
        try:
            resp = httpx.get(uri, timeout=30)
            resp.raise_for_status()
            if resp.status_code == 200:
                return
        except Exception as exp:
            LOG.info("Failed to fetch %s: %s, waiting 60s", uri, exp)
        time.sleep(60)
    LOG.warning("Failed to find upstream file %s, aborting", uri)
    sys.exit(1)


def run(tmpfp: tempfile._TemporaryFileWrapper, valid: datetime):
    """run for this valid time!"""
    for hr in range(HOURS[valid.hour] + 1):
        shr = f"{hr:02.0f}"
        if hr <= 18:
            uri = valid.strftime(
                f"{AWS}hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsubhf{shr}.grib2.idx"
            )
        else:
            uri = valid.strftime(
                f"{AWS}hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsfcf{shr}.grib2.idx"
            )
        LOG.info(uri)
        req = exponential_backoff(httpx.get, uri, timeout=30)
        if req is None or req.status_code != 200:
            LOG.info("failed to fetch %s", uri)
            if hr > 18:
                continue
            LOG.info("ABORT")
            return
        data = req.text

        offsets = []
        neednext = False
        for line in data.split("\n"):
            if line.strip() == "":
                continue
            tokens = line.split(":")
            if neednext:
                offsets[-1].append(int(tokens[1]))
                neednext = False
            if tokens[3] not in ["REFD", "CSNOW", "CICEP", "CFRZR", "CRAIN"]:
                continue
            if tokens[3] == "REFD" and tokens[4] != "1000 m above ground":
                continue
            offsets.append([int(tokens[1])])
            neednext = True

        answer = 20 if (0 < hr < 19) else 5
        if len(offsets) != answer:
            LOG.warning(
                "[%s] hr: %s offsets: %s wanted: %s",
                valid.strftime("%Y%m%d%H"),
                hr,
                offsets,
                answer,
            )
        for pr in offsets:
            headers = {"Range": f"bytes={pr[0]}-{pr[1]}"}
            req = exponential_backoff(
                httpx.get,
                uri[:-4],
                headers=headers,
                timeout=30,
            )
            if req is None:
                LOG.info("FAIL %s %s", uri[:-4], headers)
                continue
            tmpfp.write(req.content)

    tmpfp.close()
    # insert into LDM Please
    pqstr = (
        f"data a {valid:%Y%m%d%H%M} bogus model/hrrr/{valid.hour:02.0f}/"
        f"hrrr.t{valid.hour:02.0f}z.refd.grib2 grib2"
    )
    with subprocess.Popen(
        ["pqinsert", "-p", pqstr, tmpfp.name],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    ) as proc:
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            LOG.info("pqinsert failed: %s %s", stdout, stderr)
            sys.exit(1)
    os.unlink(tmpfp.name)


@click.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True}
)
@click.option("--valid", type=click.DateTime(), required=True)
@click.option(
    "--skip-recheck",
    "skiprecheck",
    is_flag=True,
    help="Skip recheck of archive",
)
def main(valid: datetime, skiprecheck: bool):
    """Go Main Go"""
    if is_archive_complete(valid):
        return
    wait_for_upstream(valid)
    with tempfile.NamedTemporaryFile("wb", delete=False) as tmpfp:
        run(tmpfp, valid.replace(tzinfo=timezone.utc))
    if skiprecheck:
        return
    # We are waiting for the archive file to be in place, so that we can
    # proceed with the next steps from hrrr_jobs.py
    for _ in range(10):
        time.sleep(60)
        if is_archive_complete(valid):
            return
        LOG.info("Waiting 60s for archive file to be complete")
    LOG.warning("Failed to find archive file for %s, aborting", valid)
    sys.exit(1)


if __name__ == "__main__":
    # do main
    main()
