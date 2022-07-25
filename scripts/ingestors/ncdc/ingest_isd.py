"""Ingest NCEI's ISH data into the IEM archives."""
import sys
import subprocess
import os

import tqdm
import requests
from pyiem.nws.products.metarcollect import to_metar
from pyiem.ncei import ds3505
from pyiem.util import get_dbconn, utc, exponential_backoff, logger

LOG = logger()
TMPDIR = "/mesonet/tmp"


class FakeTextProd:
    def __init__(self):
        """Lame."""
        self.utcnow = None
        self.valid = None
        self.nwsli_provider = {}


def set_metadata(prod, faa):
    """Need to figure out what the network, iemid are."""
    mesosite = get_dbconn("mesosite")
    cursor = mesosite.cursor()
    localid = faa[1:] if faa.startswith("K") else faa
    cursor.execute(
        "select network, tzname, iemid from stations where id = %s and "
        "network ~* 'ASOS'",
        (localid,),
    )
    if cursor.rowcount != 1:
        LOG.fatal("Failed to find station metadata!")
        sys.exit()
    (network, tzname, _iemid) = cursor.fetchone()
    prod.nwsli_provider[localid] = {"network": network, "tzname": tzname}
    mesosite.close()


def main(argv):
    """Go"""
    textprod = FakeTextProd()
    asosdb = get_dbconn("asos")
    iemdb = get_dbconn("iem")
    airforce = int(argv[1])
    wban = int(argv[2])
    faa = argv[3]
    if len(faa) == 3:
        LOG.error("Provided faa ID should be 4 chars, abort")
        return
    set_metadata(textprod, faa)
    year = max([int(argv[4]), 1928])  # database starts in 1928
    year2 = int(argv[5])
    failedyears = []
    msgs = []
    dbid = faa if len(faa) == 4 and faa[0] != "K" else faa[1:]
    for year in tqdm.tqdm(range(year, year2)):
        sts = utc(year, 1, 1)
        ets = sts.replace(year=year + 1)
        acursor = asosdb.cursor()
        icursor = iemdb.cursor()
        lfn = "%06i-%05i-%s" % (airforce, wban, year)
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
                "gunzip %s/%s.gz" % (TMPDIR, lfn),
                shell=True,
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
        for line in open(f"{TMPDIR}/{lfn}", errors="ignore", encoding="utf-8"):
            try:
                data = ds3505.parser(line.strip(), faa, add_metar=True)
            except Exception as exp:
                print(f"failed to parse line: '{line.strip()}'")
                print(exp)
                data = None
            if data is None:
                bad += 1
                continue
            if data["valid"].strftime("%Y%m%d%H%M") in current:
                skipped += 1
                continue
            textprod.valid = data["valid"]
            textprod.utcnow = data["valid"]
            mtr = to_metar(textprod, data["metar"])
            mtr.to_iemaccess(
                icursor, force_current_log=True, skip_current=True
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
