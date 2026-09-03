"""Process the GEFS onto the IEMRE grids, but only for database storage.

- We only care about the 0z run as it has the long duration forecast.

Dedicated crontab entry
"""

import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
import numpy as np
import pygrib
import requests
from affine import Affine
from psycopg2.extensions import connection
from pyiem.database import get_dbconn
from pyiem.iemre import DOMAINS as IEMRE_DOMAINS
from pyiem.iemre import reproject2iemre
from pyiem.util import logger, set_property
from tqdm import tqdm

LOG = logger()


def dl_helper(url: str, headers: dict | None = None):
    """Helper with some retries."""
    for _ in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=60)
            if resp.status_code == 503:  # Slow Down
                time.sleep(15)
                continue
            resp.raise_for_status()
            return resp
        except Exception as exp:
            LOG.warning("dl_helper failed for %s: %s", url, exp)
    raise RuntimeError(f"Failed to download {url} after 3 tries, aborting")


def download_gribs(valid: datetime, workdir: Path):
    """Do the grib download work, ufff."""
    is_interactive = sys.stdout.isatty()
    progress = tqdm(list(range(31)), disable=not is_interactive)
    for member in progress:
        gribprefix = "gec" if member == 0 else "gep"
        for fhour in range(6, 841, 6):
            progress.set_description(f"m{member}.f{fhour}")
            localfn = workdir / f"gefs.{fhour:03.0f}.m{member:02.0f}.grib2"
            if localfn.exists() and localfn.stat().st_size > 0:
                if is_interactive:
                    progress.write(f"Already have {localfn}, skip download")
                continue
            idxurl = (
                "https://noaa-gefs-pds.s3.amazonaws.com"
                f"/gefs.{valid:%Y%m%d}/{valid:%H}/atmos/pgrb2ap5"
                f"/{gribprefix}{member:02.0f}.t{valid:%H}z."
                f"pgrb2a.0p50.f{fhour:03.0f}.idx"
            )
            offsets = []
            start_byte = None
            resp = dl_helper(idxurl)
            quorum = 0
            for line in resp.text.split("\n"):
                # 3:292339:d=2026090100:RH:10 mb:390 hour fcst:ENS=low-res ctl
                tokens = line.split(":")
                if len(tokens) < 5:
                    continue
                if (
                    tokens[3] in ["RH", "TMAX", "TMIN"]
                    and tokens[4] == "2 m above ground"
                ):
                    quorum += 1
                    # Opt: our grids of interest appear to be sequential, so
                    # attempt to consolidate http requests into one, hopefully
                    if start_byte is None:
                        start_byte = int(tokens[1])
                    continue
                if start_byte is not None:
                    offsets.append((start_byte, int(tokens[1]) - 1))
                    start_byte = None

            # Just in case.
            if start_byte is not None:
                offsets.append((start_byte, start_byte + 1_000_000))

            if quorum != 3:
                raise RuntimeError(
                    f"Found only {quorum}/3 messages in {idxurl}. aborting"
                )
            griburl = idxurl.removesuffix(".idx")
            with open(localfn, "wb") as fh:
                for start, end in offsets:
                    headers = {"Range": f"bytes={start}-{end}"}
                    resp = dl_helper(griburl, headers=headers)
                    fh.write(resp.content)


def compute_daily(
    conn: connection, domain: str, valid: datetime, workdir: Path
):
    """Chunk away, one domain at a time, sigh..."""
    # Tricky here for how to compute a valid date
    # iemre US 2024-08-05 -> 2024-08-06  6 UTC
    # sa      2024-08-05 -> 2024-08-06  6 UTC  Don't have hourly
    # europe   2024-08-05 -> 2024-08-06  0 UTC
    # china    2024-08-05 -> 2024-08-05 18 UTC
    write_hour = {
        "conus": 6,
        "sa": 6,
        "europe": 0,
        "china": 18,
    }
    affine = None
    is_interactive = sys.stdout.isatty()
    progress = tqdm(list(range(31)), disable=not is_interactive)
    for member in progress:
        tmaxgrid = None
        tmingrid = None
        rhgrid = None
        quorum = 0
        for fhour in range(6, 841, 6):
            gribpath = workdir / f"gefs.{fhour:03.0f}.m{member:02.0f}.grib2"
            quorum += 1
            with pygrib.open(gribpath) as grbs:
                for grb in grbs:
                    if affine is None:
                        dx = grb["iDirectionIncrementInDegrees"]
                        # the grib data is top down
                        affine = Affine(
                            dx,
                            0.0,
                            0 - dx / 2.0,
                            0.0,
                            -dx,
                            min(
                                grb["latitudeOfFirstGridPointInDegrees"]
                                + dx / 2.0,
                                89.99,
                            ),
                        )
                    if grb.shortName == "2r":
                        if rhgrid is None:
                            rhgrid = grb.values
                        else:
                            rhgrid += grb.values
                    elif grb.shortName == "tmax":
                        if tmaxgrid is None:
                            tmaxgrid = grb.values
                        else:
                            tmaxgrid = np.where(
                                grb.values > tmaxgrid, grb.values, tmaxgrid
                            )
                    elif grb.shortName == "tmin":
                        if tmingrid is None:
                            tmingrid = grb.values
                        else:
                            tmingrid = np.where(
                                grb.values < tmingrid, grb.values, tmingrid
                            )
            fxtime = valid + timedelta(hours=fhour)
            if fxtime.hour != write_hour[domain]:
                continue
            approxlocal = (
                (fxtime - timedelta(hours=6))
                .astimezone(IEMRE_DOMAINS[domain]["tzinfo"])
                .date()
            )
            if quorum == 4:
                # Average the RH
                rhgrid = rhgrid / quorum
                tmax = reproject2iemre(
                    tmaxgrid,
                    affine,
                    "EPSG:4326",
                    domain=domain,
                )
                tmax_mask = np.ma.getmaskarray(tmax)
                tmin = reproject2iemre(
                    tmingrid,
                    affine,
                    "EPSG:4326",
                    domain=domain,
                )
                tmin_mask = np.ma.getmaskarray(tmin)
                rh = reproject2iemre(
                    rhgrid,
                    affine,
                    "EPSG:4326",
                    domain=domain,
                )
                rh_mask = np.ma.getmaskarray(rh)
                # So the IEMRE grid gid winds from SW corner -> and then ^
                cursor = conn.cursor()
                with cursor.copy(
                    "copy iemre_gefs(gid, ens_member, model_valid, valid, "
                    "high_tmpk, low_tmpk, avg_rh) from STDIN"
                ) as copy:
                    for gid, (i, j) in enumerate(np.ndindex(tmax.shape)):
                        if tmax_mask[i, j] or tmin_mask[i, j] or rh_mask[i, j]:
                            continue
                        copy.write_row(
                            (
                                gid,
                                member,
                                valid,
                                approxlocal,
                                float(tmax[i, j]),
                                float(tmin[i, j]),
                                float(rh[i, j]),
                            )
                        )
                cursor.close()
                conn.commit()
            quorum = 0
            rhgrid = None
            tmaxgrid = None
            tmingrid = None


@click.command()
@click.option(
    "--valid",
    type=click.DateTime(),
    help="Specify UTC valid time",
    required=True,
)
def main(valid: datetime):
    """Do the work."""
    valid = valid.replace(tzinfo=timezone.utc)
    # Run every hour, filter those we don't run
    if valid.hour != 0:
        LOG.info("Skipping %s hour run, only 0z is processed", valid.hour)
        return
    workdir = Path("/mesonet/tmp") / f"gefs_{valid:%Y%m%d%H}"
    workdir.mkdir(exist_ok=True, parents=True)
    download_gribs(valid, workdir)
    for domain in IEMRE_DOMAINS:
        conn = get_dbconn("iemre" if domain == "conus" else f"iemre_{domain}")
        cursor = conn.cursor()
        # Delete out existing data.
        cursor.execute(
            "DELETE from iemre_gefs where model_valid = %s",
            (valid,),
        )
        LOG.info("Removed %s rows for domain: %s", cursor.rowcount, domain)
        cursor.close()
        conn.commit()
        compute_daily(conn, domain, valid, workdir)
        set_property(f"iemre.gefs.{domain}", f"{valid:%Y-%m-%dT%H:%MZ}")

    # Blow out the work dir
    for fn in workdir.iterdir():
        fn.unlink()
    workdir.rmdir()


if __name__ == "__main__":
    main()
