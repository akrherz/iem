"""Ingest NCEI's ISH data into the IEM archives.

https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt
"""
import os
import subprocess
import sys
from unittest import mock

import requests
import tqdm
from pyiem.ncei import ds3505
from pyiem.nws.products.metarcollect import normid, to_iemaccess, to_metar
from pyiem.util import exponential_backoff, get_dbconn, logger, utc

LOG = logger()
TMPDIR = "/mesonet/tmp"


def get_metadata(faa):
    """Need to figure out what the network, iemid are."""
    mesosite = get_dbconn("mesosite")
    cursor = mesosite.cursor()
    localid = normid(faa)
    cursor.execute(
        "select tzname, iemid from stations where id = %s and "
        "network ~* 'ASOS'",
        (localid,),
    )
    if cursor.rowcount != 1:
        LOG.fatal("Failed to find station metadata!")
        sys.exit()
    (tzname, iemid) = cursor.fetchone()
    mesosite.close()
    return tzname, iemid


def main(argv):
    """Go"""
    asosdb = get_dbconn("asos")
    iemdb = get_dbconn("iem")
    airforce = int(argv[1])
    wban = int(argv[2])
    faa = argv[3]
    if len(faa) == 3:
        LOG.error("Provided faa ID should be 4 chars, abort")
        return
    tzname, iemid = get_metadata(faa)
    year = max([int(argv[4]), 1928])  # database starts in 1928
    year2 = int(argv[5])
    failedyears = []
    msgs = []
    dbid = normid(faa)
    for year in tqdm.tqdm(range(year, year2)):
        sts = utc(year, 1, 1)
        ets = sts.replace(year=year + 1)
        acursor = asosdb.cursor()
        icursor = iemdb.cursor()
        lfn = f"{airforce:06.0f}-{wban:05.0f}-{year}"
        if not os.path.isfile(f"{TMPDIR}/{lfn}"):
            uri = f"https://www1.ncdc.noaa.gov/pub/data/noaa/{year}/{lfn}.gz"
            req = exponential_backoff(requests.get, uri, timeout=30)
            if req is None or req.status_code != 200:
                LOG.info("Failed to fetch %s", uri)
                failedyears.append(year)
                continue
            with open(f"{TMPDIR}/{lfn}.gz", "wb") as fh:
                fh.write(req.content)
            subprocess.call(
                ["gunzip", f"{TMPDIR}/{lfn}.gz"],
                stderr=subprocess.PIPE,
            )
        added = 0
        bad = 0
        skipped = 0
        current = []
        # build out our current obs
        acursor.execute(
            "SELECT valid at time zone 'UTC' from alldata where "
            "station = %s and valid >= %s and valid < %s "
            "ORDER by valid ASC",
            (dbid, sts, ets),
        )
        for row in acursor:
            current.append(row[0].strftime("%Y%m%d%H%M"))
        acursor.close()
        # ignore any bad bytes, sigh
        with open(f"{TMPDIR}/{lfn}", errors="ignore", encoding="utf-8") as fh:
            for line in fh:
                try:
                    data = ds3505.parser(line.strip(), faa, add_metar=True)
                except ValueError as exp:
                    print(f"failed to parse line: '{line.strip()}'")
                    print(exp)
                    data = None
                if data is None:
                    bad += 1
                    continue
                if data["valid"].strftime("%Y%m%d%H%M") in current:
                    skipped += 1
                    continue
                textprod = mock.Mock()
                textprod.valid = data["valid"]
                textprod.utcnow = data["valid"]
                mtr = to_metar(textprod, data["metar"])
                to_iemaccess(
                    icursor,
                    mtr,
                    iemid,
                    tzname,
                    force_current_log=True,
                    skip_current=True,
                )
                added += 1
        msgs.append(
            f"  {year}: {faa} added: {added} bad: {bad} skipped: {skipped}"
        )
        icursor.close()
        iemdb.commit()
        os.unlink(f"{TMPDIR}/{lfn}")
    LOG.info(" failed years: %s", failedyears)
    LOG.info("\n".join(msgs))


if __name__ == "__main__":
    main(sys.argv)
