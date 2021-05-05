"""
 https://www.ncei.noaa.gov/data/normals-daily/1991-2020/access/
"""
import datetime
from io import StringIO

import requests
import pandas as pd
from tqdm import tqdm
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()
BASEURL = "https://www.ncei.noaa.gov/data/normals-daily/1991-2020/access"


def remove_station(sid):
    """We don't want."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "DELETE from stations where id = %s and network = 'NCEI91'",
        (sid,),
    )
    cursor.close()
    pgconn.commit()


def nona(val, minval=None):
    if pd.isna(val):
        return None
    if minval is not None and val < minval:
        return None
    return val


def ingest(pgconn, sid):
    """Ingest the data into the database!"""
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT count(*) from ncei_climate91 where station = %s",
        (sid,),
    )
    if cursor.fetchone()[0] == 366:
        return
    req = requests.get(f"{BASEURL}/{sid}.csv", timeout=30)
    if req.status_code != 200:
        LOG.info("failed to get %s", sid)
        return
    sio = StringIO()
    sio.write(req.text)
    sio.seek(0)
    df = pd.read_csv(sio)
    if (
        "DLY-TMAX-NORMAL" not in df.columns
        or "YTD-PRCP-NORMAL" not in df.columns
    ):
        remove_station(sid)
        return
    df["high"] = df["DLY-TMAX-NORMAL"]
    df["low"] = df["DLY-TMIN-NORMAL"]
    df["pcum"] = df["YTD-PRCP-NORMAL"]
    if "YTD-SNOW-NORMAL" in df.columns:
        df["scum"] = df["YTD-SNOW-NORMAL"]
        # hack for Feb 29
        df.at[59, "scum"] = df.at[58, "scum"]
        df["snow"] = df["scum"].diff()
        df.at[0, "snow"] = df.at[0, "scum"]
        df.at[59, "snow"] = df.at[58, "snow"]
    else:
        df["snow"] = 0
    df.at[59, "pcum"] = df.at[58, "pcum"]
    df["precip"] = df["pcum"].diff()
    df.at[0, "precip"] = df.at[0, "pcum"]
    df.at[59, "precip"] = df.at[58, "precip"]
    for _, row in df.iterrows():
        now = datetime.datetime(2000, row["month"], row["day"])
        cursor.execute(
            "INSERT into ncei_climate91 (station, valid, high, low, precip, "
            "snow) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                sid,
                now,
                nona(row["high"]),
                nona(row["low"]),
                nona(row["precip"], 0),
                nona(row["snow"], 0),
            ),
        )
    cursor.close()
    pgconn.commit()


def main():
    """Go main Go"""
    pgconn = get_dbconn("coop")
    nt = NetworkTable("NCEI91")
    progress = tqdm(list(nt.sts.keys()))
    for sid in progress:
        progress.set_description(sid)
        ingest(pgconn, sid)


if __name__ == "__main__":
    # Go
    main()
