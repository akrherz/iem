"""Ingest NCEI's ISH data into the IEM archives.

https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt
"""

import os
import subprocess
import sys
from unittest import mock

import click
import httpx
import pandas as pd
import tqdm
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.ncei import ds3505
from pyiem.nws.products.metarcollect import normid, to_iemaccess, to_metar
from pyiem.util import c2f, logger, utc
from sqlalchemy import text

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


@click.command()
@click.option("--airforce", type=int, required=True)
@click.option("--wban", type=int, required=True)
@click.option("--faa", type=str, required=True)
@click.option("--year1", type=int, required=True)
@click.option("--year2", type=int, required=True)
def main(airforce, wban, faa, year1, year2):
    """Go"""
    asosdb = get_dbconn("asos")
    iemdb = get_dbconn("iem")
    if len(faa) == 3:
        LOG.error("Provided faa ID should be 4 chars, abort")
        return
    tzname, iemid = get_metadata(faa)
    year1 = max(year1, 1928)  # database starts in 1928
    failedyears = []
    msgs = []
    dbid = normid(faa)
    for year in tqdm.tqdm(range(year1, year2 + 1)):
        sts = utc(year, 1, 1)
        ets = sts.replace(year=year + 1)
        icursor = iemdb.cursor()
        lfn = f"{airforce:06.0f}-{wban:05.0f}-{year}"
        if not os.path.isfile(f"{TMPDIR}/{lfn}"):
            uri = f"https://www.ncei.noaa.gov/pub/data/noaa/{year}/{lfn}.gz"
            try:
                req = httpx.get(uri, timeout=30)
                req.raise_for_status()
            except Exception:
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
        empty = 0
        deleted = 0
        with get_sqlalchemy_conn("asos") as asosconn:
            # build out our current obs
            obsdf = pd.read_sql(
                text("""
            SELECT valid, tmpf, metar, editable from alldata where
            station = :station and valid >= :sts and valid < :ets
            ORDER by valid ASC
                """),
                asosconn,
                params={"station": dbid, "sts": sts, "ets": ets},
            )
        if not obsdf.empty:
            obsdf["valid"] = obsdf["valid"].dt.tz_convert("UTC")
            obsdf = obsdf.set_index("valid")
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
                current_tmpf = None
                current_metar = None
                new_tmpf = (
                    None
                    if data["airtemp_c"] is None
                    else c2f(data["airtemp_c"])
                )
                if data["report_type"] not in ["FM-15", "FM-16"]:
                    continue
                if data["valid"].minute == 0:
                    continue
                if data["valid"] in obsdf.index:
                    if new_tmpf is None:
                        continue
                    if not obsdf.at[data["valid"], "editable"]:
                        continue
                    current_metar = obsdf.at[data["valid"], "metar"]
                    current_tmpf = obsdf.at[data["valid"], "tmpf"]
                if (
                    pd.notna(current_tmpf)
                    and new_tmpf is not None
                    and abs(current_tmpf - new_tmpf) < 1
                ):
                    skipped += 1
                    continue
                textprod = mock.Mock()
                textprod.valid = data["valid"]
                textprod.utcnow = data["valid"]
                mtr = to_metar(textprod, data["metar"])
                # Avoid KDSM 150559Z AUTO RMK IEM_DS3505
                if len(mtr.code) == 32:
                    empty += 1
                    continue
                if current_metar is not None:
                    acursor = asosdb.cursor()
                    # Life choices, if this is first, we need to delete lots
                    if data["valid"].day == 1:
                        acursor.execute(
                            f"delete from t{data['valid'].year} "
                            "where station = %s and valid >= %s "
                            "and valid < %s",
                            (
                                dbid,
                                data["valid"].replace(hour=0, minute=0),
                                data["valid"].replace(hour=8, minute=0),
                            ),
                        )
                        deleted += acursor.rowcount
                    acursor.execute(
                        f"delete from t{data['valid'].year} "
                        "where station = %s and valid = %s",
                        (dbid, data["valid"]),
                    )
                    deleted += acursor.rowcount
                    acursor.close()
                    asosdb.commit()
                    print(
                        f"{data['valid']} {current_tmpf} -> {new_tmpf} | "
                        f"{current_metar} -> {mtr.code}"
                    )
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
            f"  {year}: {faa} added: {added} bad: {bad} skipped: {skipped} "
            f"empty: {empty} deleted: {deleted}"
        )
        icursor.close()
        iemdb.commit()
        os.unlink(f"{TMPDIR}/{lfn}")
    LOG.info(" failed years: %s", failedyears)
    LOG.info("\n".join(msgs))


if __name__ == "__main__":
    main()
