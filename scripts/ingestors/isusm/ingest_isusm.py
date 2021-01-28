"""ISUSM ingest."""
import datetime
import os
import subprocess
import traceback

import inotify.adapters
import pytz
from metpy.units import units
from metpy.calc import dewpoint_from_relative_humidity
from pyiem.observation import Observation
from pyiem.util import get_dbconn, logger, convert_value, c2f
import numpy as np
import pandas as pd

LOG = logger()
DIRPATH = "/var/opt/CampbellSci/LoggerNet"
STOREPATH = "/mesonet/data/isusm"
TSOIL_COLS = [
    "tsoil_c_avg",
    "t06_c_avg",
    "t12_c_avg",
    "t24_c_avg",
    "t50_c_avg",
]
TABLES = {
    "MinSI": "sm_minute",
    "Min5SI": "sm_minute",
    "HrlySI": "sm_hourly",
    "DailySI": "sm_daily",
}
VARCONV = {
    "timestamp": "valid",
    "vwc06_avg": "vwc_06_avg",
    "vwc_avg6in": "vwc_06_avg",
    "vwc12_avg": "vwc_12_avg",
    "vwc_avg12in": "vwc_12_avg",
    "vwc24_avg": "vwc_24_avg",
    "vwc_avg24in": "vwc_24_avg",
    "vwc_avg30in": "calcvwc30_avg",
    "vwc_avg40in": "calcvwc40_avg",
    "vwc50_avg": "vwc_50_avg",
    "calcvwc06_avg": "calc_vwc_06_avg",
    "calcvwc12_avg": "calc_vwc_12_avg",
    "calcvwc24_avg": "calc_vwc_24_avg",
    "calcvwc50_avg": "calc_vwc_50_avg",
    "outofrange06": "P06OutOfRange",
    "outofrange12": "P12OutOfRange",
    "outofrange24": "P24OutOfRange",
    "outofrange50": "P50OutOfRange",
    "ws_ms_s_wvt": "ws_mps_s_wvt",
    "ec6in": "ec06",
    "ec12in": "ec12",
    "ec_2in": "ec2",
    "ec_4in": "ec4",
    "ec_8in": "ec8",
    "ec_12in": "ec12",
    "ec_16in": "ec16",
    "ec_20in": "ec20",
    "ec_24in": "ec24",
    "ec_30in": "ec30",
    "ec_40in": "ec40",
    "vwc_2in": "vwc2",
    "vwc_4in": "vwc4",
    "vwc_8in": "vwc8",
    "vwc_12in": "vwc12",
    "vwc_16in": "vwc16",
    "vwc_20in": "vwc20",
    "vwc_24in": "vwc24",
    "vwc_30in": "vwc30",
    "vwc_40in": "vwc40",
    "temp_2in": "t02_c_avg",
    "temp_4in": "t04_c_avg",
    "temp_8in": "t08_c_avg",
    "temp_12in": "t12_c_avg",
    "temp_16in": "t16_c_avg",
    "temp_20in": "t20_c_avg",
    "temp_24in": "t24_c_avg",
    "temp_30in": "t30_c_avg",
    "temp_40in": "t40_c_avg",
    "ec24in": "ec24",
    "rh_avg": "rh",
    "temp_avg6in": "t06_c_avg",
    "temp_avg12in": "t12_c_avg",
    "temp_avg24in": "t24_c_avg",
    "temp_avg30in": "t30_c_avg",
    "temp_avg40in": "t40_c_avg",
    "bp_mmhg_avg": "bpres_avg",
    "bp_mb": "bpres_avg",
    "battv": "battv_min",
    "encrh": "encrh_avg",
}
STATIONS = {
    "Calumet": "CAMI4",
    "AEAFarm": "BOOI4",
    "Wellman": "WMNI4",
    "Sibley": "SBEI4",
    "Nashua": "NASI4",
    "Lewis": "OKLI4",
    "WestPoint": "WTPI4",
    "Doon": "DONI4",
    "Kanawha": "KNAI4",
    "Greenfield": "GREI4",
    "Newell": "NWLI4",
    "Ames": "AEEI4",
    "Castana": "CNAI4",
    "Chariton": "CHAI4",
    "Crawfordsville": "CRFI4",
    "Muscatine": "FRUI4",
    "CedarRapids": "CIRI4",
    "Marcus": "MCSI4",
    "AmesFinch": "AMFI4",
    # Temporary?
    # 'REFI4': 'Adel',
    # Vineyward
    "AmesHort": "AHTI4",
    "TasselRidge": "OSTI4",
    "Bankston": "BNKI4",
    "Inwood": "CSII4",
    "Glenwood": "GVNI4",
    "Masonville": "TPOI4",
}


def make_time(string):
    """Convert a CST timestamp in the file to a datetime"""
    tstamp = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    tstamp = tstamp.replace(tzinfo=pytz.FixedOffset(-360))
    return tstamp


def qcval(df, colname, floor, ceiling):
    """Make sure the value falls within some bounds"""
    df.loc[df[colname] < floor, colname] = floor
    df.loc[df[colname] > ceiling, colname] = ceiling
    return np.where(
        np.logical_or(df[colname] == floor, df[colname] == ceiling), "B", None
    )


def qcval2(df, colname, floor, ceiling):
    """Make sure the value falls within some bounds, Null if not"""
    df.loc[df[colname] < floor, colname] = np.nan
    df.loc[df[colname] > ceiling, colname] = np.nan
    return np.where(pd.isnull(df[colname]), "B", None)


def minute_iemaccess(df):
    """Process dataframe into iemaccess."""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    for _i, row in df.iterrows():
        # Update IEMAccess, pandas.Timestamp causes grief
        ob = Observation(row["station"], "ISUSM", row["valid"].to_pydatetime())
        tmpc = units("degC") * row["tair_c_avg_qc"]
        tmpf = tmpc.to(units("degF")).m
        if -50 < tmpf < 140:
            ob.data["tmpf"] = tmpf
            relh = units("percent") * row["rh_avg_qc"]
            ob.data["relh"] = relh.m
            ob.data["dwpf"] = (
                dewpoint_from_relative_humidity(tmpc, relh).to(units("degF")).m
            )
        # database srad is W/ms2
        ob.data["srad"] = row["slrkj_tot_qc"] / 60.0 * 1000.0
        ob.data["pcounter"] = row["rain_in_tot_qc"]
        ob.data["sknt"] = convert_value(
            row["ws_mph_s_wvt_qc"], "mile / hour", "knot"
        )
        if "ws_mph_max" in df.columns:
            ob.data["gust"] = convert_value(
                row["ws_mph_max_qc"], "mile / hour", "knot"
            )
        ob.data["drct"] = row["winddir_d1_wvt_qc"]
        if "tsoil_c_avg" in df.columns:
            ob.data["c1tmpf"] = c2f(row["tsoil_c_avg_qc"])
        ob.data["c2tmpf"] = c2f(row["t12_c_avg_qc"])
        ob.data["c3tmpf"] = c2f(row["t24_c_avg_qc"])
        if "t50_c_avg" in df.columns:
            ob.data["c4tmpf"] = c2f(row["t50_c_avg_qc"])
        if "calcvwc12_avg" in df.columns:
            ob.data["c2smv"] = row["calcvwc12_avg_qc"] * 100.0
        if "calcvwc24_avg" in df.columns:
            ob.data["c3smv"] = row["calcvwc24_avg_qc"] * 100.0
        if "calcvwc50_avg" in df.columns:
            ob.data["c4smv"] = row["calcvwc50_avg_qc"] * 100.0
        ob.save(cursor)
    cursor.close()
    pgconn.commit()


def process(path, fn):
    """Attempt to do something with the file we found."""
    tokens = fn.split("_", 2)
    station = STATIONS[tokens[0]]
    tabletype = tokens[1]
    tablename = TABLES[tabletype]
    df = pd.read_csv(
        os.path.join(path, fn), skiprows=[0, 2, 3], na_values=["NAN", "-100"]
    )
    if df.empty:
        return
    # convert all columns to lowercase
    df.columns = map(str.lower, df.columns)
    # rename columns to rectify differences
    if tabletype != "MinSI":
        df = df.rename(columns=VARCONV)
    else:
        df = df.rename(columns={"timestamp": "valid"})
    df["valid"] = df["valid"].apply(make_time)
    if tabletype == "DailySI":
        # This is kludgy, during CDT, timestamp is 1 AM, CST, midnight
        df["valid"] = df["valid"].dt.date - datetime.timedelta(days=1)
        df["rain_mm_tot"] = convert_value(
            df["rain_in_tot"], "inch", "millimeter"
        )
        df = df.drop("rain_in_tot", axis=1)
        df["slrmj_tot"] = df["slrw_avg"] * 86400.0 / 1000000.0
        df = df.drop("slrw_avg", axis=1)
    elif tabletype == "HrlySI":
        df["slrmj_tot"] = df["slrw_avg"] * 3600.0 / 1000000.0
        df = df.drop("slrw_avg", axis=1)
        df["rain_mm_tot"] = convert_value(
            df["rain_in_tot"], "inch", "millimeter"
        )
        df = df.drop("rain_in_tot", axis=1)
        df["ws_mps_s_wvt"] = df["ws_mph_s_wvt"] * 0.44704
        df = df.drop("ws_mph_s_wvt", axis=1)
    elif tabletype == "MinSI":
        # Rework solar rad
        df["slrkj_tot"] = df["slrw_avg"] * 60.0 / 1000.0
        df = df.drop("slrw_avg", axis=1)

    df = df.drop("record", axis=1)
    # Create _qc and _f columns
    for colname in df.columns:
        if colname == "valid":
            continue
        if tabletype != "MinSI" and colname == "rain_in_tot":
            # Database currently only has mm column :/
            df["rain_mm_tot"] = convert_value(
                df["rain_in_tot"], "inch", "millimeter"
            )
            df["rain_mm_tot_qc"] = convert_value(
                df["rain_in_tot"], "inch", "millimeter"
            )
            df["rain_mm_tot_f"] = None
        df["%s_qc" % (colname,)] = df[colname]
        if colname.startswith("calc_vwc"):
            df["%s_f" % (colname,)] = qcval(
                df, "%s_qc" % (colname,), 0.01, 0.7
            )
        elif colname in TSOIL_COLS:
            df["%s_f" % (colname,)] = qcval2(
                df, "%s_qc" % (colname,), -20.0, 37.0
            )
        else:
            df["%s_f" % (colname,)] = None

    df["station"] = station
    if "ws_mph_tmx" in df.columns:
        df["ws_mph_tmx"] = df["ws_mph_tmx"].apply(make_time)

    # Begin database work.
    pgconn = get_dbconn("isuag")
    icursor = pgconn.cursor()
    if tabletype == "MinSI":
        tablename = "sm_minute"
    # Convert any nan values to None for purposes of database work
    df2 = df.replace({np.nan: None})
    # Delete away any old data
    for _, row in df2.iterrows():
        icursor.execute(
            f"SELECT 1 from {tablename} WHERE station = %s and valid = %s",
            (row["station"], row["valid"]),
        )
        if icursor.rowcount == 0:
            icursor.execute(
                f"INSERT into {tablename} (station, valid) VALUES (%s, %s)",
                (row["station"], row["valid"]),
            )
        opts = []
        params = []
        for col in df.columns:
            opts.append(f"{col} = %s")
            params.append(row[col])

        params.extend([row["station"], row["valid"]])
        # Do the update
        icursor.execute(
            f"UPDATE {tablename} SET {','.join(opts)} WHERE "
            "station = %s and valid = %s",
            params,
        )
        if icursor.rowcount != 1:
            LOG.info(
                "station %s valid: %s table: %s did non-1 rows",
                row["station"],
                row["valid"],
                tablename,
            )
    icursor.close()
    pgconn.commit()
    if tabletype == "MinSI":
        minute_iemaccess(df)


def main():
    """Go Main Go."""
    inotif = inotify.adapters.Inotify()
    inotif.add_watch(DIRPATH)
    try:
        for event in inotif.event_gen():
            if event is None:
                continue
            (_header, type_names, watch_path, fn) = event
            # LOG.debug("fn: %s type_names: %s", fn, str(type_names))
            if "IN_CLOSE_WRITE" not in type_names:
                continue
            if not fn.endswith(".dat"):
                continue
            try:
                process(watch_path, fn)
            except Exception as exp:
                LOG.error("filename: %s errored: %s", fn, exp)
                with open("%s/%s.error" % (STOREPATH, fn), "w") as fp:
                    fp.write(str(exp) + "\n")
                    traceback.print_exc(file=fp)
                # Copy the file to an error location
                errordir = os.path.join(STOREPATH, "error.d")
                if not os.path.isdir("error.d"):
                    os.makedirs(errordir)
                subprocess.call(
                    "cp %s %s" % (os.path.join(watch_path, fn), errordir),
                    shell=True,
                )
            finally:
                subprocess.call(
                    "mv %s/%s %s/%s" % (watch_path, fn, STOREPATH, fn),
                    shell=True,
                )
    finally:
        inotif.remove_watch(DIRPATH)


if __name__ == "__main__":
    main()
