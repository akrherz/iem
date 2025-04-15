"""Ingest the ISU FEEL Farm data.

Run from RUN_10AFTER.sh
"""

import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
from pyiem.database import get_dbconn, get_dbconnc
from pyiem.observation import Observation
from pyiem.util import c2f, convert_value, logger

LOG = logger()
BASE = "/mesonet/home/mesonet/ot/ot0005/incoming/Pierson"
CST = ZoneInfo("Etc/GMT+6")


def get_starttimes(cursor) -> tuple[date, datetime]:
    """Figure out when we have data"""
    cursor.execute(
        "SELECT max(valid at time zone 'UTC+06') from feel_data_hourly"
    )
    row = cursor.fetchone()
    hstart = row[0].replace(tzinfo=CST)

    cursor.execute("SELECT max(valid) from feel_data_daily")
    row = cursor.fetchone()
    dstart = row[0]

    return dstart, hstart


def ingest(cursor):
    """Lets do something"""

    dstart, hstart = get_starttimes(cursor)
    LOG.info("dstart: %s hstart: %s", dstart, hstart)
    if dstart is None:
        dstart = date(1980, 1, 1)
    if hstart is None:
        hstart = datetime(1980, 1, 1)
    fn = f"{BASE}/{date.today():%Y}/ISU_Feel_Daily.dat"
    # If this file does not exist, try the previous year's file
    if not os.path.isfile(fn):
        fn = f"{BASE}/{date.today().year - 1}/ISU_Feel_Daily.dat"
        if not os.path.isfile(fn):
            LOG.warning("Double failure to find %s", fn)
            return

    df = pd.read_csv(
        fn, header=0, skiprows=[0, 2, 3], quotechar='"', on_bad_lines="warn"
    )

    iconn, icursor = get_dbconnc("iem")
    for _, row in df.iterrows():
        ts = datetime.strptime(row["TIMESTAMP"][:10], "%Y-%m-%d")
        if ts.date() <= dstart:
            continue
        # We have to do this because the data is in UTC-6
        ob = Observation(
            "OT0011", "OT", ts.replace(tzinfo=ZoneInfo("Etc/GMT+6"))
        )
        ob.data["max_tmpf"] = c2f(row["AirTemp_Max"])
        ob.data["min_tmpf"] = c2f(row["AirTemp_Min"])
        ob.data["pday"] = convert_value(row["Rain_Tot"], "mm", "inch")
        ob.data["srad_mj"] = row["SolarRad_MJ_Tot"]
        ob.data["max_sknt"] = convert_value(
            row["Windspeed_Max"], "mps", "knots"
        )
        ob.save(icursor)
        cursor.execute(
            """
            INSERT into feel_data_daily(
            valid, AirTemp_Max, AirTemp_Min, Rain_Tot,
            Windspeed_Max, SolarRad_MJ_Tot) VALUES (%s, %s, %s, %s,
            %s, %s)
        """,
            (
                ts,
                row["AirTemp_Max"],
                row["AirTemp_Min"],
                row["Rain_Tot"],
                row["Windspeed_Max"],
                row["SolarRad_MJ_Tot"],
            ),
        )

    fn = f"{BASE}/{date.today().year}/ISU_Feel_Hourly.dat"
    # If this file does not exist, try the previous year's file
    if not os.path.isfile(fn):
        fn = f"{BASE}/{date.today().year - 1}/ISU_Feel_Hourly.dat"
        if not os.path.isfile(fn):
            LOG.warning("Double failure to find %s", fn)
            return
    df = pd.read_csv(
        fn, header=0, skiprows=[0, 2, 3], quotechar='"', on_bad_lines="warn"
    )

    for _, row in df.iterrows():
        ts = datetime.strptime(row["TIMESTAMP"][:13], "%Y-%m-%d %H").replace(
            tzinfo=CST
        )
        if ts <= hstart:
            continue
        LOG.info("Hourly ingest: %s", ts)
        # We have to do this because the data is in UTC-6
        ob = Observation("OT0011", "OT", ts)
        ob.data["tmpf"] = c2f(row["AirTemp_Avg"])
        ob.data["relh"] = row["RH_Avg"]
        ob.data["drct"] = row["WindDir_Avg"]
        ob.data["sknt"] = convert_value(row["Windspeed_Avg"], "mps", "knots")
        ob.data["srad"] = row["SolarRad_W_Avg"]
        ob.data["phour"] = convert_value(row["Rain_Tot"], "mm", "inch")
        ob.save(icursor)

        cursor.execute(
            """
            INSERT into feel_data_hourly(
            valid, BattVolt_Avg, PanTemp_Avg, AirTemp_Avg,
            RH_Avg, sat_vp_Avg, act_vp_Avg, WindDir_Avg, Windspeed_Avg,
            SolarRad_mV_Avg, SolarRad_W_Avg, Soil_Temp_5_Avg, Rain_Tot,
            LWS1_Avg, LWS2_Avg, LWS3_Avg, LWS1_Ohms, LWS2_Ohms,
            LWS3_Ohms, LWS1_Ohms_Hst, LWS2_Ohms_Hst, LWS3_Ohms_Hst) VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                ts,
                row["BattVolt_Avg"],
                row["PanTemp_Avg"],
                row["AirTemp_Avg"],
                row["RH_Avg"],
                row["sat_vp_Avg"],
                row["act_vp_Avg"],
                row["WindDir_Avg"],
                row["Windspeed_Avg"],
                row["SolarRad_mV_Avg"],
                row["SolarRad_W_Avg"],
                row["Soil_Temp_5_Avg"],
                row["Rain_Tot"],
                row["LWS1_Avg"],
                row["LWS2_Avg"],
                row["LWS3_Avg"],
                row["LWS1_Ohms"],
                row["LWS2_Ohms"],
                row["LWS3_Ohms"],
                row["LWS1_Ohms_Hst"],
                row["LWS2_Ohms_Hst"],
                row["LWS3_Ohms_Hst"],
            ),
        )

    icursor.close()
    iconn.commit()
    iconn.close()


def main():
    """Go Main"""
    pgconn = get_dbconn("other")
    cursor = pgconn.cursor()
    ingest(cursor)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
