"""Ingest NCEI's ISH data into the IEM archives."""
import sys
import subprocess
import os

import tqdm
import requests
from pyiem.ncei import ds3505
from pyiem.util import get_dbconn, utc, exponential_backoff, logger

LOG = logger()
ADD_ONLY = True
TMPDIR = "/mesonet/tmp"


def main(argv):
    """Go"""
    pgconn = get_dbconn("asos")
    airforce = int(argv[1])
    wban = int(argv[2])
    faa = argv[3]
    if len(faa) == 3:
        LOG.error("Provided faa ID should be 4 chars, abort")
        return
    year = max([int(argv[4]), 1928])  # database starts in 1928
    year2 = int(argv[5])
    failedyears = []
    msgs = []
    dbid = faa if len(faa) == 4 and faa[0] != "K" else faa[1:]
    for year in tqdm.tqdm(range(year, year2)):
        sts = utc(year, 1, 1)
        ets = sts.replace(year=year + 1)
        cursor = pgconn.cursor()
        lfn = "%06i-%05i-%s" % (airforce, wban, year)
        if not os.path.isfile("%s/%s" % (TMPDIR, lfn)):
            uri = "https://www1.ncdc.noaa.gov/pub/data/noaa/%s/%s.gz" % (
                year,
                lfn,
            )
            req = exponential_backoff(requests.get, uri, timeout=30)
            if req is None or req.status_code != 200:
                LOG.info("Failed to fetch %s", uri)
                failedyears.append(year)
                continue
            with open("%s/%s.gz" % (TMPDIR, lfn), "wb") as fh:
                fh.write(req.content)
            subprocess.call(
                "gunzip %s/%s.gz" % (TMPDIR, lfn),
                shell=True,
                stderr=subprocess.PIPE,
            )
        added = 0
        bad = 0
        removed = 0
        skipped = 0
        current = []
        if ADD_ONLY:
            # build out our current obs
            cursor.execute(
                "SELECT valid at time zone 'UTC' from alldata where "
                "station = %s and valid >= %s and valid < %s "
                "ORDER by valid ASC",
                (dbid, sts, ets),
            )
            for row in cursor:
                current.append(row[0].strftime("%Y%m%d%H%M"))
        # ignore any bad bytes, sigh
        for line in open("%s/%s" % (TMPDIR, lfn), errors="ignore"):
            try:
                data = ds3505.parser(line.strip(), faa, add_metar=True)
            except Exception as exp:
                print(f"failed to parse line: '{line.strip()}'")
                print(exp)
                data = None
            if data is None:
                bad += 1
                continue
            if added == 0 and not ADD_ONLY:
                cursor.execute(
                    "DELETE from alldata where station = %s and "
                    "valid >= %s and valid < %s",
                    (dbid, sts, ets),
                )
                if cursor.rowcount > 0:
                    LOG.info("deleted %s rows for %s", cursor.rowcount, dbid)
                removed = cursor.rowcount
            if ADD_ONLY and data["valid"].strftime("%Y%m%d%H%M") in current:
                skipped += 1
                continue
            res = ds3505.sql(cursor, faa, data)
            if res is None:
                skipped += 1
            else:
                added += 1
        msgs.append(
            ("  %s: %s added: %s removed: %s bad: %s" " skipped: %s")
            % (year, faa, added, removed, bad, skipped)
        )
        cursor.close()
        pgconn.commit()
        os.unlink("%s/%s" % (TMPDIR, lfn))
    LOG.info(" failed years: %s", failedyears)
    LOG.info("\n".join(msgs))


if __name__ == "__main__":
    main(sys.argv)
