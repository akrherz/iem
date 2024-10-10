"""
Stop gap ingest from SPC since rucsoundings is down

called from RUN_10_AFTER.sh for 00z and 12z
"""

import datetime
import sys
from typing import Optional
from zoneinfo import ZoneInfo

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger
from tqdm import tqdm

LOG = logger()


class RAOB:
    """Simple class representing a RAOB profile"""

    def __init__(self):
        """constructor"""
        self.station = None
        self.valid = None
        self.release_time = None
        self.profile = []
        self.wind_units = None
        self.hydro_level = None
        self.maxwd_level = None
        self.tropo_level = None

    def conv_hhmm(self, raw):
        """Convert string to timestamp"""
        if raw == "99999":
            return None
        if int(raw) < 100:
            return self.valid.replace(hour=0, minute=0) + datetime.timedelta(
                minutes=int(raw)
            )
        minute = int(raw[-2:])
        hour = int(raw[:-2])
        if minute > 59:
            minute = minute - 60
            hour += 1
        ts = self.valid.replace(hour=hour, minute=minute)
        if ts.hour > 20 and self.valid.hour < 2:
            ts -= datetime.timedelta(days=1)
        return ts

    def conv_speed(self, raw):
        """convert sped to mps units"""
        if raw in ["99999", "-9999.00"]:
            return None
        if self.wind_units == "kt":
            return float(raw) * 0.5144
        return float(raw)

    def __str__(self):
        """override str()"""
        return (
            f"RAOB from {self.station} valid {self.valid} "
            f"with {len(self.profile)} levels"
        )

    def database_save(self, txn):
        """Save this to the provided database cursor"""
        txn.execute(
            "SELECT fid from raob_flights where station = %s and valid = %s",
            (self.station, self.valid),
        )
        if txn.rowcount == 0:
            txn.execute(
                "INSERT into raob_flights (valid, station, release_time, "
                "hydro_level, maxwd_level, tropo_level, computed) "
                "values (%s,%s,%s,%s,%s,%s, 'f') RETURNING fid",
                (
                    self.valid,
                    self.station,
                    self.release_time,
                    self.hydro_level,
                    self.maxwd_level,
                    self.tropo_level,
                ),
            )
        fid = txn.fetchone()[0]
        # update ingested_at timestamp
        txn.execute(
            "UPDATE raob_flights SET ingested_at = now() where fid = %s",
            (fid,),
        )
        txn.execute("DELETE from raob_profile where fid = %s", (fid,))
        if txn.rowcount > 0 and self.valid.hour in [0, 12]:
            LOG.info(
                "RAOB del %s rows for sid: %s valid: %s",
                txn.rowcount,
                self.station,
                self.valid.strftime("%Y-%m-%d %H"),
            )
        table = f"raob_profile_{self.valid.year}"
        for d in self.profile:
            txn.execute(
                f"INSERT into {table} (fid, ts, levelcode, pressure, height, "
                "tmpc, dwpc, drct, smps, bearing, range_miles) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    fid,
                    d["ts"],
                    d["levelcode"],
                    d["pressure"],
                    d["height"],
                    d["tmpc"],
                    d["dwpc"],
                    d["drct"],
                    d["smps"],
                    d["bearing"],
                    d["range"],
                ),
            )


def conv(raw: str):
    """Convert raw string to database value"""
    val = float(raw)
    if val < -9998:
        return None
    return float(raw)


def parse(raw, sid):
    """Parse the raw data and yield RAOB objects"""
    rob = RAOB()
    meat = raw[raw.find("%RAW%") + 5 : raw.find("%END%")].strip()
    # Sigh, duplicate entries
    last_pressure = None
    for line in meat.split("\n"):
        tokens = line.strip().split(",")
        if len(tokens) != 6:
            continue
        pressure = conv(tokens[0])
        if pressure is None or pressure == last_pressure:
            continue
        last_pressure = pressure
        rob.profile.append(
            {
                "levelcode": 4,  # sigh
                "pressure": pressure,
                "height": conv(tokens[1]),
                "tmpc": conv(tokens[2]),
                "dwpc": conv(tokens[3]),
                "drct": conv(tokens[4]),
                "smps": conv(tokens[5]),
                "ts": None,
                "bearing": None,
                "range": None,
            }
        )
    return rob


def main(valid, station):
    """Run for the given valid time!"""
    LOG.info("running for %s", valid)
    nt = NetworkTable("RAOB")
    dbconn = get_dbconn("raob")
    # check what we have
    with get_sqlalchemy_conn("raob") as conn:
        obs = pd.read_sql(
            f"""SELECT station, locked, count(*),
            sum(case when smps is null then 1 else 0 end) as nullcnt from
            raob_flights f JOIN raob_profile_{valid.year} p
            ON (f.fid = p.fid) where valid = %s GROUP by station, locked
            ORDER by station ASC
            """,
            conn,
            params=(valid,),
            index_col="station",
        )
    obs["added"] = 0
    sids = list(nt.sts.keys())
    if station in nt.sts:
        sids = [station]

    progress = tqdm(sids, disable=not sys.stdout.isatty())
    for sid in progress:
        # skip virtual sites
        if sid.startswith("_"):
            continue
        if sid in obs.index:
            # skip sites that are locked
            if obs.at[sid, "locked"]:
                LOG.warning("skipping locked %s", sid)
                continue
            # arb decision that we have enough data already
            if obs.at[sid, "nullcnt"] < 10 < obs.at[sid, "count"]:
                continue
        progress.set_description(sid)
        sid3 = sid[1:] if sid.startswith("K") else sid
        uri = (
            "https://www.spc.noaa.gov/exper/soundings/"
            f"{valid:%y%m%d%H}_OBS/{sid3}.txt"
        )
        try:
            resp = httpx.get(uri, timeout=30)
            resp.raise_for_status()
        except Exception as exp:
            LOG.info("dl failed %s for %s with %s", sid, valid, exp)
            continue
        cursor = dbconn.cursor()
        try:
            rob = parse(resp.text, sid)
            if rob is None:
                continue
            rob.station = sid
            rob.valid = valid
            obs.at[sid, "added"] = len(rob.profile)
            rob.database_save(cursor)
        except Exception as exp:
            fn = f"/tmp/{sid}_{valid:%Y%m%d%H%M}_fail"
            LOG.warning("FAIL %s %s %s, content at %s", sid, valid, exp, fn)
            with open(fn, "wb") as fh:
                fh.write(resp.content)
        finally:
            cursor.close()
            dbconn.commit()
    LOG.info("%s entered %s levels of data", valid, obs["added"].sum())
    df2 = obs[obs["count"] == 0]
    if len(df2.index) > 40:
        LOG.info("%s high missing count of %s", valid, len(df2.index))


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
@click.option("--station", type=str, default=None)
def frontend(valid: datetime, station: Optional[str]):
    """Figure out what we need to do here!"""
    valid = valid.replace(tzinfo=ZoneInfo("UTC"))
    main(valid, station)


if __name__ == "__main__":
    frontend()
