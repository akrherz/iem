"""ISUSM ingest."""
from io import StringIO
import datetime
import traceback
import subprocess

import inotify.adapters
import pytz
from pyiem.observation import Observation
from pyiem.datatypes import temperature, humidity, speed
import pyiem.meteorology as met
from pyiem.util import get_dbconn
import numpy as np
import pandas as pd

DIRPATH = "/var/opt/CampbellSci/LoggerNet"
STOREPATH = "/mesonet/data/isusm"
TSOIL_COLS = [
    "tsoil_c_avg",
    "t06_c_avg",
    "t12_c_avg",
    "t24_c_avg",
    "t50_c_avg",
]
TABLES = {"MinSI": "sm_minute", "HrlySI": "sm_hourly", "DailySI": "sm_daily"}
VARCONV = {
    "timestamp": "valid",
    "vwc06_avg": "vwc_06_avg",
    "vwc_avg6in": "vwc_06_avg",
    "vwc12_avg": "vwc_12_avg",
    "vwc_avg12in": "vwc_12_avg",
    "vwc24_avg": "vwc_24_avg",
    "vwc_avg24in": "vwc_24_avg",
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
    "ec_24in": "ec24",
    "ec24in": "ec24",
    "rh_avg": "rh",
    "temp_avg6in": "t06_c_avg",
    "temp_avg12in": "t12_c_avg",
    "temp_avg24in": "t24_c_avg",
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
    """Convert a time in the file to a datetime"""
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
        # Update IEMAccess
        # print nwsli, valid
        ob = Observation(row["station"], "ISUSM", row["valid"])
        tmpc = temperature(row["tair_c_avg_qc"], "C")
        if tmpc.value("F") > -50 and tmpc.value("F") < 140:
            ob.data["tmpf"] = tmpc.value("F")
            relh = humidity(row["rh_avg_qc"], "%")
            ob.data["relh"] = relh.value("%")
            ob.data["dwpf"] = met.dewpoint(tmpc, relh).value("F")
        # database srad is W/ms2
        ob.data["srad"] = row["slrkj_tot_qc"] / 60.0 * 1000.0
        ob.data["pcounter"] = row["rain_in_tot_qc"]
        ob.data["sknt"] = speed(row["ws_mph_s_wvt_qc"], "MPH").value("KT")
        if "ws_mph_max" in df.columns:
            ob.data["gust"] = speed(row["ws_mph_max_qc"], "MPH").value("KT")
        ob.data["drct"] = row["winddir_d1_wvt_qc"]
        if "tsoil_c_avg" in df.columns:
            ob.data["c1tmpf"] = temperature(row["tsoil_c_avg_qc"], "C").value(
                "F"
            )
        ob.data["c2tmpf"] = temperature(row["t12_c_avg_qc"], "C").value("F")
        ob.data["c3tmpf"] = temperature(row["t24_c_avg_qc"], "C").value("F")
        if "t50_c_avg" in df.columns:
            ob.data["c4tmpf"] = temperature(row["t50_c_avg_qc"], "C").value(
                "F"
            )
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
    df = pd.read_csv(path + "/" + fn, skiprows=[0, 2, 3], na_values=["NAN"])
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
        # Rework the valid column into the appropriate date
        df["valid"] = df["valid"].dt.date - datetime.timedelta(days=1)
        df["rain_mm_tot"] = df["rain_in_tot"] * 25.4
        df = df.drop("rain_in_tot", axis=1)
        df["slrmj_tot"] = df["slrw_avg"] * 86400.0 / 1000000.0
        df = df.drop("slrw_avg", axis=1)
    elif tabletype == "HrlySI":
        df["slrmj_tot"] = df["slrw_avg"] * 3600.0 / 1000000.0
        df = df.drop("slrw_avg", axis=1)
        df["rain_mm_tot"] = df["rain_in_tot"] * 25.4
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
        elif tabletype != "MinSI" and colname == "rain_in_tot":
            # Database currently only has mm column :/
            df["rain_mm_tot"] = df["rain_in_tot"] * 25.4
            df["rain_mm_tot_qc"] = df["rain_in_tot"] * 25.4
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
    output = StringIO()
    df.to_csv(output, sep="\t", header=False, index=False)
    output.seek(0)
    pgconn = get_dbconn("isuag")
    icursor = pgconn.cursor()
    if tabletype == "MinSI":
        # partitioned tables
        tablename = "sm_minute_%s" % (df.iloc[0]["valid"].strftime("%Y"),)
    icursor.copy_from(output, tablename, columns=df.columns, null="")
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
            if "IN_CLOSE_WRITE" not in type_names:
                continue
            if not fn.endswith(".dat"):
                continue
            try:
                process(watch_path, fn)
            except Exception as exp:
                with open("%s/%s.error" % (STOREPATH, fn), "w") as fp:
                    fp.write(str(exp) + "\n")
                    traceback.print_exc(file=fp)
            finally:
                subprocess.call(
                    "mv %s/%s %s/%s" % (watch_path, fn, STOREPATH, fn),
                    shell=True,
                )
    finally:
        inotif.remove_watch(DIRPATH)


if __name__ == "__main__":
    main()
