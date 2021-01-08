"""Ingest the Fisher/Porter rain gage data from NCDC

    Run from RUN_2AM.sh for 3, 6, and 12 months in the past
    on the 15th each month
"""
import sys
import datetime
import os

import requests
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, exponential_backoff, logger

LOG = logger()


def process(tmpfn):
    """Process a file of data"""
    pgconn = get_dbconn("other")
    nt = NetworkTable("IA_HPD")
    data = []
    for line in open(tmpfn):
        tokens = line.split(",")
        if len(tokens) < 9:
            continue
        if tokens[0] not in nt.sts:
            continue
        sid = tokens[0]
        cst = datetime.datetime.strptime(
            tokens[1] + " " + tokens[2], "%Y/%m/%d %H:%M:%S"
        )
        counter = tokens[4].strip()
        tmpc = tokens[5].strip()
        battery = tokens[8].strip()
        data.append(
            dict(sid=sid, cst=cst, counter=counter, tmpc=tmpc, battery=battery)
        )
    if not data:
        LOG.info("No data found for %s", tmpfn)
        return
    df = pd.DataFrame(data)
    sids = df["sid"].unique()
    LOG.info("Found %s records from %s stations", len(data), len(sids))
    for sid in sids:
        cursor = pgconn.cursor()
        df2 = df[df["sid"] == sid]
        maxts = df2["cst"].max()
        mints = df2["cst"].min()
        # Delete out old data
        cursor.execute(
            "DELETE from hpd_alldata where station = '%s' and "
            "valid >= '%s-06' and valid <= '%s-06'"
            % (
                sid,
                mints.strftime("%Y-%m-%d %H:%M:%S"),
                maxts.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        if cursor.rowcount > 0:
            LOG.info(" - removed  %s rows for sid: %s", cursor.rowcount, sid)
        counter = None
        for (_, row) in df2.iterrows():
            if counter is None:
                counter = float(row["counter"])
            if counter is not None and row["counter"] is not None:
                precip = float(row["counter"]) - counter
                if precip < 0:
                    precip = 0
            else:
                precip = 0
            if precip > 1:
                LOG.info(
                    ("sid: %s cst: %s precip: %s counter1: %s counter2: %s"),
                    sid,
                    row["cst"],
                    precip,
                    counter,
                    row["counter"],
                )
            counter = float(row["counter"])
            tbl = "hpd_%s" % (row["cst"] + datetime.timedelta(hours=6)).year
            cursor.execute(
                f"INSERT into {tbl} (station, valid, counter, tmpc, "
                "battery, calc_precip) VALUES "
                "('%s', '%s-06', %s, %s, %s, %s)"
                % (
                    sid,
                    row["cst"].strftime("%Y-%m-%d %H:%M:%S"),
                    "null" if row["counter"] == "NaN" else row["counter"],
                    "null" if row["tmpc"] == "" else row["tmpc"],
                    "null" if row["battery"] == "" else row["battery"],
                    "null" if pd.isnull(precip) else precip,
                )
            )
        LOG.info(" + inserted %s rows for sid: %s", len(df2), sid)
        cursor.close()
        pgconn.commit()


def dowork(valid):
    """Process a month's worth of data"""
    uri = valid.strftime(
        "https://www1.ncdc.noaa.gov/pub/data/hpd/data/hpd_%Y%m.csv"
    )
    tmpfn = valid.strftime("/mesonet/tmp/hpd_%Y%m.csv")
    if not os.path.isfile(tmpfn):
        LOG.info("Downloading %s from NCDC", tmpfn)
        req = exponential_backoff(requests.get, uri, timeout=60)
        if req is None or req.status_code != 200:
            LOG.info("dlerror")
            return
        with open(tmpfn, "wb") as fh:
            fh.write(req.content)

    process(tmpfn)
    os.unlink(tmpfn)


def main(argv):
    """Go Main Go"""
    valid = datetime.datetime(int(argv[1]), int(argv[2]), 1)
    dowork(valid)


if __name__ == "__main__":
    main(sys.argv)
