"""Process the GHCN data.

    $ python ingest_ghcn.py  # runs for a random state
    $ python ingest_ghcn.py IA0200  # runs for a given station
    $ python ingest_ghcn.py ALL  # runs over entire database
    $ python ingest_ghcn.py IA  # runs for given state
    $ python ingest_ghcn.py IA bogus  # allows inserts to happen

 https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/USC00130200.dly
 https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt

 ID            1-11   Character
YEAR         12-15   Integer
MONTH        16-17   Integer
ELEMENT      18-21   Character
VALUE1       22-26   Integer
MFLAG1       27-27   Character
QFLAG1       28-28   Character
SFLAG1       29-29   Character
VALUE2       30-34   Integer
MFLAG2       35-35   Character
QFLAG2       36-36   Character
SFLAG2       37-37   Character
  .           .          .
  .           .          .
  .           .          .
VALUE31    262-266   Integer
MFLAG31    267-267   Character
QFLAG31    268-268   Character
SFLAG31    269-269   Character

    PRCP = Precipitation (tenths of mm)
    SNOW = Snowfall (mm)
    SNWD = Snow depth (mm)
    TMAX = Maximum temperature (tenths of degrees C)
    TMIN = Minimum temperature (tenths of degrees C)
"""
import os
import datetime
import sys
import re

import requests
import pandas as pd
from pandas.io.sql import read_sql
import numpy as np
from pyiem.reference import TRACE_VALUE, state_names
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, exponential_backoff, logger, c2f, mm2inch

LOG = logger()
PGCONN = get_dbconn("coop")

BASEDIR = "/mesonet/tmp"
BASE = datetime.date(1850, 1, 1)
TODAY = datetime.date.today()
DATARE = re.compile(
    r"""
(?P<id>[A-Z0-9]{11})
(?P<year>[0-9]{4})
(?P<month>[0-9]{2})
(?P<element>[A-Z0-9]{4})
(?P<value1>[0-9\- ]{5})(?P<flag1>...)
(?P<value2>[0-9\- ]{5})(?P<flag2>...)
(?P<value3>[0-9\- ]{5})(?P<flag3>...)
(?P<value4>[0-9\- ]{5})(?P<flag4>...)
(?P<value5>[0-9\- ]{5})(?P<flag5>...)
(?P<value6>[0-9\- ]{5})(?P<flag6>...)
(?P<value7>[0-9\- ]{5})(?P<flag7>...)
(?P<value8>[0-9\- ]{5})(?P<flag8>...)
(?P<value9>[0-9\- ]{5})(?P<flag9>...)
(?P<value10>[0-9\- ]{5})(?P<flag10>...)
(?P<value11>[0-9\- ]{5})(?P<flag11>...)
(?P<value12>[0-9\- ]{5})(?P<flag12>...)
(?P<value13>[0-9\- ]{5})(?P<flag13>...)
(?P<value14>[0-9\- ]{5})(?P<flag14>...)
(?P<value15>[0-9\- ]{5})(?P<flag15>...)
(?P<value16>[0-9\- ]{5})(?P<flag16>...)
(?P<value17>[0-9\- ]{5})(?P<flag17>...)
(?P<value18>[0-9\- ]{5})(?P<flag18>...)
(?P<value19>[0-9\- ]{5})(?P<flag19>...)
(?P<value20>[0-9\- ]{5})(?P<flag20>...)
(?P<value21>[0-9\- ]{5})(?P<flag21>...)
(?P<value22>[0-9\- ]{5})(?P<flag22>...)
(?P<value23>[0-9\- ]{5})(?P<flag23>...)
(?P<value24>[0-9\- ]{5})(?P<flag24>...)
(?P<value25>[0-9\- ]{5})(?P<flag25>...)
(?P<value26>[0-9\- ]{5})(?P<flag26>...)
(?P<value27>[0-9\- ]{5})(?P<flag27>...)
(?P<value28>[0-9\- ]{5})(?P<flag28>...)
(?P<value29>[0-9\- ]{5})(?P<flag29>...)
(?P<value30>[0-9\- ]{5})(?P<flag30>...)
(?P<value31>[0-9\- ]{5})(?P<flag31>...)
""",
    re.VERBOSE,
)


def get_file(station):
    """Download the file from NCEI, if necessary!"""
    uri = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/{station}.dly"
    localfn = "%s/%s.dly" % (BASEDIR, station)
    if not os.path.isfile(localfn):
        LOG.info("dl from NCEI station: %s", station)
        req = exponential_backoff(requests.get, uri, timeout=30)
        if req is None:
            LOG.info("ingest_ghcn download failed for %s", uri)
            return None
        with open(localfn, "wb") as fp:
            fp.write(req.content)
    else:
        LOG.info("%s is cached...", localfn)
    return localfn


def get_days_for_month(day):
    """Compute the number of days this month"""
    nextmo = day + datetime.timedelta(days=35)
    nextmo = nextmo.replace(day=1)
    return (nextmo - day).days


def varconv(val, element):
    """Convert NCDC to something we use in the database"""
    ret = None
    if element in ["TMAX", "TMIN"]:
        fv = round(c2f(float(val) / 10.0), 0)
        ret = None if (fv < -100 or fv > 150) else fv
    elif element in ["PRCP"]:
        fv = round(mm2inch(float(val) / 10.0), 2)
        ret = None if fv < 0 else fv
    elif element in ["SNOW", "SNWD"]:
        fv = round(mm2inch(float(val)), 1)
        ret = None if fv < 0 else fv
    return ret


def get_obs(metadata):
    """Generate the observation data frame"""
    # The GHCN station ID is based on what the database has for its 11 char
    fn = get_file(metadata["ncdc81"])
    if fn is None:
        return None
    rows = []
    for line in open(fn):
        m = DATARE.match(line)
        if m is None:
            continue
        data = m.groupdict()
        if data["element"] not in ["TMAX", "TMIN", "PRCP", "SNOW", "SNWD"]:
            continue
        day = datetime.date(int(data["year"]), int(data["month"]), 1)
        days = get_days_for_month(day)
        for i in range(1, days + 1):
            day = day.replace(day=i)
            # We don't want data in the future!
            if day >= TODAY:
                continue
            rows.append(
                [
                    day,
                    data["element"],
                    varconv(data["value%s" % (i,)], data["element"]),
                    data["flag%s" % (i,)][0],
                    data["flag%s" % (i,)][1],
                    data["flag%s" % (i,)][2],
                ]
            )
    os.unlink(fn)
    df = pd.DataFrame(
        rows, columns=["date", "element", "value", "mflag", "qflag", "sflag"]
    )
    df["date"] = pd.to_datetime(df["date"])
    # Replace trace values
    df.loc[df["mflag"] == "T", "value"] = TRACE_VALUE
    # If data is flagged, set it to NaN
    df.loc[df["qflag"] != " ", "value"] = np.nan
    # pivot our dataset
    return df[["date", "element", "value"]].pivot(
        index="date", columns="element", values="value"
    )


def process(station, metadata, allow_inserts):
    """Lets process something, stat

    ['TMAX', 'TMIN', 'TOBS', 'PRCP', 'SNOW', 'SNWD', 'EVAP', 'MNPN', 'MXPN',
     'WDMV', 'DAEV', 'MDEV', 'DAWM', 'MDWM', 'WT05', 'SN01', 'SN02', 'SN03',
     'SX01', 'SX02', 'SX03', 'MDPR', 'MDSF', 'SN51', 'SN52', 'SN53', 'SX51',
     'SX52', 'SX53', 'WT01', 'SN31', 'SN32', 'SN33', 'SX31', 'SX32', 'SX33']
    """
    cursor = PGCONN.cursor()
    obs = get_obs(metadata)
    if obs is None:
        LOG.info("Failing to process %s as obs is None", station)
        return
    for col in ["TMAX", "TMIN", "PRCP", "SNOW", "SNWD"]:
        if col not in obs.columns:
            LOG.info("Obs missing for column: %s", col)
            obs[col] = None

    table = "alldata_%s" % (station[:2],)
    current = read_sql(
        f"SELECT day, high, low, precip, snow, snowd from {table} "
        "where station = %s ORDER by day ASC",
        PGCONN,
        params=(station,),
        index_col=None,
    )
    current["day"] = pd.to_datetime(current["day"])
    current = current.set_index("day")
    # join the tables
    df = obs.join(current, how="left")
    # Loop over our result
    cnts = {"updates": 0, "adds": 0, "inserts_skipped": 0}
    for dt, row in df.iterrows():
        date = datetime.date(dt.year, dt.month, dt.day)
        work = []
        temp_estimated = True
        precip_estimated = True
        for dbcol, obcol in zip(
            ["high", "low", "precip", "snow", "snowd"],
            ["TMAX", "TMIN", "PRCP", "SNOW", "SNWD"],
        ):
            if pd.isna(row[obcol]) or row[obcol] == row[dbcol]:
                continue
            if dbcol in ["high", "low"]:
                temp_estimated = False
            elif dbcol == "precip":
                precip_estimated = False
            work.append(" %s = %s " % (dbcol, row[obcol]))
            if dbcol in ["high", "low"] and abs(row[dbcol] - row[obcol]) > 5:
                LOG.debug(
                    "%5s %s large diff %s %s",
                    dbcol,
                    date,
                    row[obcol],
                    row[dbcol],
                )
            if dbcol == "precip" and abs(row[dbcol] - row[obcol]) > 0.25:
                LOG.debug(
                    "%5s %s large diff %s %s",
                    dbcol,
                    date,
                    row[obcol],
                    row[dbcol],
                )
        if not work:
            continue
        cursor.execute(
            f"UPDATE {table} SET {','.join(work)}, precip_estimated = %s, "
            "temp_estimated = %s WHERE station = %s and day = %s",
            (precip_estimated, temp_estimated, station, date),
        )
        if cursor.rowcount == 1:
            cnts["updates"] += 1
            continue
        if not allow_inserts:
            cnts["inserts_skipped"] += 1
            continue
        cnts["adds"] += 1
        # Adding a row
        cursor.execute(
            f"INSERT into {table} (station, day, sday, year, month, high, "
            "low, precip, snow, snowd, precip_estimated, temp_estimated) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                station,
                date,
                "%02i%02i" % (date.month, date.day),
                date.year,
                date.month,
                None if pd.isna(row["TMAX"]) else row["TMAX"],
                None if pd.isna(row["TMIN"]) else row["TMIN"],
                None if pd.isna(row["PRCP"]) else row["PRCP"],
                None if pd.isna(row["SNOW"]) else row["SNOW"],
                None if pd.isna(row["SNWD"]) else row["SNWD"],
                precip_estimated,
                temp_estimated,
            ),
        )

    LOG.info(
        "%s adds: %s skipped: %s updates: %s",
        station,
        cnts["adds"],
        cnts["inserts_skipped"],
        cnts["updates"],
    )
    cursor.close()
    PGCONN.commit()


def main(argv):
    """go main go"""
    if len(argv) == 1:
        # Run for our linear random state
        states = list(state_names.keys())
        states.sort()
        doy = int(datetime.date.today().strftime("%j"))
        station = states[doy % len(states)]
    else:
        station = argv[1]
    allow_inserts = len(argv) == 3
    if len(station) == 2:
        # we have a state!
        nt = NetworkTable("%sCLIMATE" % (station,))
        for sid in nt.sts:
            if sid[2:] == "0000" or sid[2] in ["C", "T"]:
                continue
            process(sid, nt.sts[sid], allow_inserts)
    elif station == "ALL":
        for state in state_names:
            nt = NetworkTable("%sCLIMATE" % (state,))
            for sid in nt.sts:
                if sid[2:] == "0000" or sid[2] in ["C", "T"]:
                    continue
                process(sid, nt.sts[sid], allow_inserts)
    else:
        nt = NetworkTable("%sCLIMATE" % (station[:2],))
        process(sys.argv[1], nt.sts[station], allow_inserts)


if __name__ == "__main__":
    main(sys.argv)
