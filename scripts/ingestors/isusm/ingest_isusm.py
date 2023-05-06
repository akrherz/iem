"""ISUSM ingest."""
import datetime
import os
import subprocess
import traceback

import inotify.adapters
import numpy as np
import pandas as pd
import pytz
from metpy.calc import dewpoint_from_relative_humidity
from metpy.units import units
from pyiem.observation import Observation
from pyiem.util import c2f, convert_value, get_dbconn, logger, mm2inch

LOG = logger()
DIRPATH = "/var/opt/CampbellSci/LoggerNet"
STOREPATH = "/mesonet/data/isusm"
TSOIL_COLS = [
    "t4_c_avg",
    "t6_c_avg",
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
    "tsoil_c_avg": "t4_c_avg",
    "timestamp": "valid",
    "vwc12_avg": "vwc_12_avg",
    "vwc_avg12in": "vwc_12_avg",
    "vwc24_avg": "vwc_24_avg",
    "vwc_avg24in": "vwc_24_avg",
    "vwc_avg30in": "calcvwc30_avg",  # TODO
    "vwc_avg40in": "calcvwc40_avg",
    "vwc50_avg": "vwc_50_avg",
    "calcvwc12_avg": "vwc12",
    "calcvwc24_avg": "vwc24",
    "calcvwc50_avg": "vwc50",
    "outofrange12": "p12outofrange",
    "outofrange24": "p24outofrange",
    "outofrange50": "p50outofrange",
    "ws_ms_s_wvt": "ws_mps_s_wvt",
    "ec12in": "ec12",
    "ec_2in": "sv_ec2",
    "ec_4in": "sv_ec4",
    "ec_8in": "sv_ec8",
    "ec_12in": "sv_ec12",
    "ec_14in": "sv_ec14",
    "ec_16in": "sv_ec16",
    "ec_20in": "sv_ec20",
    "ec_24in": "sv_ec24",
    "ec_28in": "sv_ec28",
    "ec_30in": "sv_ec30",
    "ec_32in": "sv_ec32",
    "ec_36in": "sv_ec36",
    "ec_40in": "sv_ec40",
    "ec_42in": "sv_ec42",
    "ec_52in": "sv_ec52",
    "vwc_2in": "sv_vwc2",
    "vwc_4in": "sv_vwc4",
    "vwc_8in": "sv_vwc8",
    "vwc_12in": "sv_vwc12",
    "vwc_14in": "sv_vwc14",
    "vwc_16in": "sv_vwc16",
    "vwc_20in": "sv_vwc20",
    "vwc_24in": "sv_vwc24",
    "vwc_28in": "sv_vwc28",
    "vwc_30in": "sv_vwc30",
    "vwc_32in": "sv_vwc32",
    "vwc_36in": "sv_vwc36",
    "vwc_40in": "sv_vwc40",
    "vwc_42in": "sv_vwc42",
    "vwc_52in": "sv_vwc52",
    "temp_2in": "sv_t2",
    "temp_4in": "sv_t4",
    "temp_8in": "sv_t8",
    "temp_12in": "sv_t12",
    "temp_14in": "sv_t14",
    "temp_16in": "sv_t16",
    "temp_20in": "sv_t20",
    "temp_24in": "sv_t24",
    "temp_28in": "sv_t28",
    "temp_30in": "sv_t30",
    "temp_32in": "sv_t32",
    "temp_36in": "sv_t36",
    "temp_40in": "sv_t40",
    "temp_42in": "sv_t42",
    "temp_52in": "sv_t52",
    "ec24in": "ec24",
    "rh": "rh_avg",
    "temp_avg12in": "t12_c_avg",
    "temp_avg24in": "t24_c_avg",
    "temp_avg30in": "t30_c_avg",
    "temp_avg40in": "t40_c_avg",
    "bp_mmhg_avg": "bpres_avg",
    "bp_mb": "bpres_avg",
    "battv": "battv_min",
    "encrh": "encrh_avg",
    "ws_mph_s_wvt": "ws_mph",
}
STATIONS = {
    "Sutherland": "CAMI4",
    "Calumet": "CAMI4",  # legacy, renamed on 21 March 2022
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
    "AmesKitchen": "AKCI4",
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
INVERSION = {
    "AEAInversion": "BOOI4",
    "SutherlandInversion": "CAMI4",
    "CalumetInversion": "CAMI4",  # legacy, renamed on 21 March 2022
    "CrawfordsvilleInversion": "CRFI4",
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


def do_inversion(filename, nwsli):
    """Process Inversion Station Data."""
    df = pd.read_csv(
        filename,
        skiprows=[0, 2, 3],
        na_values=["NAN", "INF"],
        encoding="ISO-8859-1",
    )
    # convert all columns to lowercase
    df.columns = map(str.lower, df.columns)
    df["valid"] = df["timestamp"].apply(make_time)
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT max(valid) from sm_inversion where station = %s",
        (nwsli,),
    )
    maxts = cursor.fetchone()[0]
    if maxts is not None:
        df = df[df["valid"] > maxts]
    for _, row in df.iterrows():
        cursor.execute(
            "INSERT into sm_inversion(station, valid, tair_15_c_avg, "
            "tair_15_c_avg_qc, tair_5_c_avg, tair_5_c_avg_qc, "
            "tair_10_c_avg, tair_10_c_avg_qc, ws_ms_avg, ws_ms_avg_qc, "
            "ws_ms_max, ws_ms_max_qc, duration) VALUES (%s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, %s, %s, %s, 1)",
            (
                nwsli,
                row["valid"],
                row["t15_avg"],
                row["t15_avg"],
                row["t5_avg"],
                row["t5_avg"],
                row["t10_avg"],
                row["t10_avg"],
                row["ws_ms_avg"],
                row["ws_ms_avg"],
                row["ws_ms_max"],
                row["ws_ms_max"],
            ),
        )
    # LOG.debug("Inserted %s inversion rows for %s", len(df.index), nwsli)
    cursor.close()
    pgconn.commit()


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
            row["ws_mph_qc"], "mile / hour", "knot"
        )
        if "ws_mph_max" in df.columns:
            ob.data["gust"] = convert_value(
                row["ws_mph_max_qc"], "mile / hour", "knot"
            )
        ob.data["drct"] = row["winddir_d1_wvt_qc"]
        for j, col in enumerate(["4", "12", "24"]):
            if f"t{col}_c_avg" in df.columns:
                ob.data[f"c{j + 1}tmpf"] = c2f(row[f"t{col}_c_avg_qc"])
        if "t50_c_avg" in df.columns:
            ob.data["c4tmpf"] = c2f(row["t50_c_avg_qc"])
        if "vwc12" in df.columns:
            ob.data["c2smv"] = row["vwc12_qc"] * 100.0
        if "vwc24" in df.columns:
            ob.data["c3smv"] = row["vwc24_qc"] * 100.0
        if "vwc50" in df.columns:
            ob.data["c4smv"] = row["vwc50_qc"] * 100.0
        ob.save(cursor)
    cursor.close()
    pgconn.commit()


def process(fullfn):
    """Attempt to do something with the file we found."""
    tokens = os.path.basename(fullfn).split("_", 2)
    tabletype = tokens[1]
    if tokens[0].find("Inversion") > 0:
        station = INVERSION[tokens[0]]
        if tabletype == "MinSI":
            do_inversion(fullfn, station)
        return
    station = STATIONS[tokens[0]]
    tablename = TABLES[tabletype]
    df = pd.read_csv(
        fullfn,
        skiprows=[0, 2, 3],
        na_values=["NAN", "-100", "INF"],
        encoding="ISO-8859-1",
    )
    if df.empty:
        return
    # convert all columns to lowercase
    df.columns = map(str.lower, df.columns)
    # rename columns to rectify differences
    if tabletype != "MinSI":  # TODO, yikes
        df = df.rename(columns=VARCONV)
    else:
        df = df.rename(
            columns={
                "timestamp": "valid",
                "tsoil_c_avg": "t4_c_avg",
                "calcvwc12_avg": "vwc12",
                "calcvwc24_avg": "vwc24",
                "calcvwc50_avg": "vwc50",
                "ws_mph_s_wvt": "ws_mph",
            }
        )
    df["valid"] = df["valid"].apply(make_time)
    for col in ["rain_mm_tot", "rain_mm_2_tot"]:
        if col in df.columns:
            df[col.replace("_mm_", "_in_")] = mm2inch(df[col])
    df = df.drop(
        [
            "rain_mm_tot",
            "rain_mm_2_tot",
            "winddir_sd1_wvt",
        ],
        axis=1,
        errors="ignore",
    )
    if "ws_mps_s_wvt" in df.columns:
        df = df.assign(
            ws_mph=lambda df_: df_["ws_mps_s_wvt"] * 2.23694,
        ).drop(
            columns=["ws_mps_s_wvt"],
        )

    if tabletype == "DailySI":
        # This is kludgy, during CDT, timestamp is 1 AM, CST, midnight
        df["valid"] = df["valid"].dt.date - datetime.timedelta(days=1)
        df["slrkj_tot"] = df["slrw_avg"] * 86400.0 / 1000.0
        # Remove un-needed data
        df = df.drop(
            ["slrw_avg", "solarradcalc", "nancounttot", "slrmj_tot"],
            axis=1,
            errors="ignore",
        )
    elif tabletype == "HrlySI":
        df["slrkj_tot"] = df["slrw_avg"] * 3600.0 / 1000.0
        df = df.drop(
            [
                "slrw_avg",
                "solarradcalc",
                "p12outofrange",
                "p24outofrange",
                "p50outofrange",
            ],
            axis=1,
            errors="ignore",
        )
    elif tabletype == "MinSI":
        # Rework solar rad
        df["slrkj_tot"] = df["slrw_avg"] * 60.0 / 1000.0
        df = df.drop(["slrw_avg", "solarradcalc"], axis=1, errors="ignore")

    df = df.drop("record", axis=1)
    # Create _qc and _f columns
    for colname in df.columns:
        if colname == "valid":
            continue
        df[f"{colname}_qc"] = df[colname]
        if colname.startswith("vwc"):
            df[f"{colname}_f"] = qcval(df, f"{colname}_qc", 0.01, 0.7)
        elif colname in TSOIL_COLS:
            df[f"{colname}_f"] = qcval2(df, f"{colname}_qc", -20.0, 37.0)
        else:
            df[f"{colname}_f"] = None

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
    for event in inotif.event_gen():
        if event is None:
            continue
        (_header, type_names, watch_path, fn) = event
        # LOG.debug("fn: %s type_names: %s", fn, str(type_names))
        if "IN_CLOSE_WRITE" not in type_names:
            continue
        if not fn.endswith(".dat"):
            continue
        fullfn = os.path.join(watch_path, fn)
        try:
            process(fullfn)
        except Exception as exp:
            LOG.error("filename: %s errored: %s", fn, exp)
            errorfn = os.path.join(STOREPATH, f"{fn}.error")
            with open(errorfn, "w", encoding="utf8") as fp:
                fp.write(f"{exp}\n")
                traceback.print_exc(file=fp)
            # Copy the file to an error location
            errordir = os.path.join(STOREPATH, "error.d")
            if not os.path.isdir(errordir):
                os.makedirs(errordir)
            subprocess.call(["cp", fullfn, errordir])
        finally:
            storefn = os.path.join(STOREPATH, fn)
            # check that we not over-write data
            if os.path.isfile(storefn):
                _i = 0
                while _i < 100 and os.path.isfile(storefn):
                    LOG.info("Destination %s file exists", storefn)
                    storefn = os.path.join(STOREPATH, f"{fn}.{_i}")
                    _i += 1
            subprocess.call(["mv", fullfn, storefn])


if __name__ == "__main__":
    main()
