"""Download and process the scan dataset.

The data is provided in a standard local timestamp, yikes.
"""

import datetime
import sys
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests
from metpy.calc import dewpoint_from_relative_humidity
from metpy.units import units
from pyiem.network import Table as NetworkTable
from pyiem.observation import Observation
from pyiem.util import convert_value, get_dbconnc, logger, utc
from tqdm import tqdm

LOG = logger()
SERVICE = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data"
ALLCOLS = (
    "RHUM  SMS2  SMS20  SMS4  SMS40  SMS8   SRADV  STO2  STO20  STO4  STO40 "
    "STO8  TOBS  WDIRV  WSPDV  WSPDX PCPN"
).split()
MAPPING = {
    "RHUM": "relh",
    "SMS2": "c1smv",
    "SMS4": "c2smv",
    "SMS8": "c3smv",
    "SMS20": "c4smv",
    "SMS40": "c5smv",
    "STO2": "c1tmpf",
    "STO4": "c2tmpf",
    "STO8": "c3tmpf",
    "STO20": "c4tmpf",
    "STO40": "c5tmpf",
    "SRADV": "srad",
    "TOBS": "tmpf",
    "WDIRV": "drct",
    "WSPDV": "sknt",
    "WSPDX": "gust",
    "PCPN": "phour",
}


def save_row(sid, meta, valid, row, icursor, scursor):
    """
    Save away our data into IEM Access
    """
    iem = Observation(iemid=meta["iemid"], valid=valid, tzname=meta["tzname"])
    for key, val in MAPPING.items():
        iem.data[val] = row[key] if not pd.isna(row[key]) else None
    iem.data["dwpf"] = row["dwpf"]
    # Old data should not go through this logic as we will have a daily update
    if valid > (utc() - datetime.timedelta(hours=23)):
        if not iem.save(icursor):
            LOG.info("iemaccess sid: %s ts: %s updated no rows", sid, valid)

    scursor.execute(
        "DELETE from alldata WHERE station = %s and valid = %s",
        (sid, valid),
    )
    scursor.execute(
        """INSERT into alldata(station, valid, tmpf, dwpf, srad, sknt, drct,
        relh, c1tmpf, c2tmpf, c3tmpf, c4tmpf, c5tmpf,
        c1smv, c2smv, c3smv, c4smv, c5smv, phour) VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s)""",
        (
            sid,
            valid,
            iem.data["tmpf"],
            iem.data["dwpf"],
            iem.data["srad"],
            iem.data["sknt"],
            iem.data["drct"],
            iem.data["relh"],
            iem.data["c1tmpf"],
            iem.data["c2tmpf"],
            iem.data["c3tmpf"],
            iem.data["c4tmpf"],
            iem.data["c5tmpf"],
            iem.data["c1smv"],
            iem.data["c2smv"],
            iem.data["c3smv"],
            iem.data["c4smv"],
            iem.data["c5smv"],
            iem.data["phour"],
        ),
    )


def load_times(icursor):
    """
    Load the latest ob times from the database
    """
    # Always force a bit of reprocessing
    icursor.execute(
        "SELECT t.id, valid - '2 hours'::interval as ts "
        "from current c, stations t WHERE "
        "t.iemid = c.iemid and t.network = 'SCAN'"
    )
    data = {}
    for row in icursor:
        data[row["id"]] = row["ts"]
    return data


def main(argv):
    """Go Main Go"""
    nt = NetworkTable("SCAN", only_online=False)
    SCAN, scursor = get_dbconnc("scan")
    ACCESS, icursor = get_dbconnc("iem")
    reprocessing = len(argv) == 4
    params = {}
    sts = datetime.datetime.now() - datetime.timedelta(days=1)
    if len(argv) == 4:
        sts = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]))
    basets = sts.replace(tzinfo=ZoneInfo("UTC")) - datetime.timedelta(days=2)
    ets = sts + datetime.timedelta(days=1)
    params["beginDate"] = sts.strftime("%Y-%m-%d %H:%M")
    params["endDate"] = ets.strftime("%Y-%m-%d %H:%M")
    params["duration"] = "HOURLY"
    params["centralTendencyType"] = "NONE"
    params["elements"] = "STO:*,SMS:*,PRCP,RHUM,SRADV,TOBS,WDIRV,WSPDV,WSPDX"
    params["returnFlags"] = "false"
    params["returnOriginalValues"] = "false"
    params["returnSuspectData"] = "false"
    params["periodRef"] = "END"

    maxts = load_times(icursor)
    progress = tqdm(nt.sts.items(), disable=not sys.stdout.isatty())
    for sid, meta in progress:
        progress.set_description(sid)
        offset = datetime.timedelta(
            hours=(0 - int(meta["attributes"]["AWDB.DATA_TIME_ZONE"]))
        )
        remote_id = int(sid[1:])
        params["stationTriplets"] = f"{remote_id}:{meta['state']}:SCAN"
        try:
            req = requests.get(SERVICE, params=params, timeout=30)
            if req.status_code != 200:
                LOG.info("Got %s for url %s", req.status_code, req.url)
                continue
            response = req.json()
        except Exception as exp:
            LOG.info("Failed to download: %s %s", sid, exp)
            continue
        rows = []
        for entry in response:
            for data in entry["data"]:
                if data["stationElement"]["ordinal"] != 1:
                    continue
                varname = data["stationElement"]["elementCode"]
                if varname in ["STO", "SMS"]:
                    depth = 0 - data["stationElement"]["heightDepth"]
                    varname = f"{varname}{depth}"
                for val in data["values"]:
                    valid = (
                        datetime.datetime.strptime(
                            val["date"][:16], "%Y-%m-%d %H:%M"
                        )
                        + offset
                    ).replace(tzinfo=ZoneInfo("UTC"))
                    if not reprocessing and valid < maxts.get(sid, basets):
                        continue
                    value = val["value"]
                    if varname == "RHUM" and not 1 <= value <= 100:
                        continue
                    rows.append(
                        {"valid": valid, "varname": varname, "value": value}
                    )
        if not rows:
            continue
        df = pd.DataFrame(rows).pivot(
            index="valid", columns="varname", values="value"
        )
        # Only unit conversion is the MPH to KTS
        for col in ["WSPDV", "WSPDX"]:
            if col in df.columns:
                df[col] = convert_value(df[col], "mph", "kts")
        # Ensure that all the columns we need are present
        for col in ALLCOLS:
            if col not in df.columns:
                df[col] = np.nan
        if df["TOBS"].isna().all() or df["RHUM"].isna().all():
            df["dwpf"] = np.nan
        else:
            df["dwpf"] = (
                dewpoint_from_relative_humidity(
                    units("degF") * df["TOBS"].values,
                    units("percent") * df["RHUM"].values,
                )
                .to(units("degF"))
                .m
            )
        for valid, row in df.iterrows():
            save_row(sid, meta, valid, row, icursor, scursor)
        icursor.close()
        scursor.close()
        ACCESS.commit()
        SCAN.commit()
        icursor = ACCESS.cursor()
        scursor = SCAN.cursor()

    icursor.close()
    scursor.close()
    ACCESS.commit()
    SCAN.commit()


if __name__ == "__main__":
    main(sys.argv)
