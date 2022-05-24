"""
    LEGACY ISU SOIL MOISTURE INGEST!

 Run from RUN_5MIN.sh
"""
# stdlib
import datetime
import os
import sys
import subprocess
import tempfile
import io

# Third party
import psycopg2
import pytz
import numpy as np
import pandas as pd
from metpy.units import units
from metpy.calc import dewpoint_from_relative_humidity
from pyiem.observation import Observation
from pyiem.util import get_dbconn, logger, convert_value, c2f, mm2inch, utc

LOG = logger()
ISUAG = get_dbconn("isuag")

ACCESS = get_dbconn("iem")

EVENTS = {"reprocess_solar": False, "days": [], "reprocess_temps": False}
VARCONV = {
    "tsoil_c_avg": "t4_c_avg",
    "timestamp": "valid",
    "vwc_avg6in": "vwc4",  # Unique to Masonville, call it 4 inch
    "temp_avg6in": "t4_c_avg",  # Unique to Masonville
    "ec6in": "ec4",  # Unique to Masonville
    "vwc12_avg": "vwc_12_avg",
    "vwc24_avg": "vwc_24_avg",
    "vwc50_avg": "vwc_50_avg",
    "calcvwc12_avg": "vwc12",
    "calcvwc24_avg": "vwc24",
    "calcvwc50_avg": "vwc50",
    "outofrange06": "p06outofrange",
    "outofrange12": "p12outofrange",
    "outofrange24": "p24outofrange",
    "outofrange50": "p50outofrange",
    "ws_ms_s_wvt": "ws_mps_s_wvt",
    "bp_mmhg_avg": "bpres_avg",
    "bp_mb_avg": "bpres_avg",
    "rh": "rh_avg",
    "ec12in": "ec12",
    "ec_12in": "ec12",
    "ec24in": "ec24",
    "ec_24in": "ec24",
    "ec50in": "ec50",
    "ec4in": "ec4",
}
VARCONV_JEFF = {
    "ec_2in": "sv_ec2",
    "ec_4in": "sv_ec4",
    "ec_8in": "sv_ec8",
    "ec_12in": "sv_ec12",
    "ec_16in": "sv_ec16",
    "ec_20in": "sv_ec20",
    "ec_24in": "sv_ec24",
    "ec_30in": "sv_ec30",
    "ec_40in": "sv_ec40",
    "vwc_2in": "sv_vwc2",
    "vwc_4in": "sv_vwc4",
    "vwc_8in": "sv_vwc8",
    "vwc_12in": "sv_vwc12",
    "vwc_16in": "sv_vwc16",
    "vwc_20in": "sv_vwc20",
    "vwc_24in": "sv_vwc24",
    "vwc_30in": "sv_vwc30",
    "vwc_40in": "sv_vwc40",
    "vwc_avg2in": "sv_vwc2",
    "vwc_avg4in": "sv_vwc4",
    "vwc_avg8in": "sv_vwc8",
    "vwc_avg12in": "sv_vwc12",
    "vwc_avg16in": "sv_vwc16",
    "vwc_avg20in": "sv_vwc20",
    "vwc_avg24in": "sv_vwc24",
    "vwc_avg30in": "sv_vwc30",
    "vwc_avg40in": "sv_vwc40",
    "temp_avg2in": "sv_t2",
    "temp_avg4in": "sv_t4",
    "temp_avg8in": "sv_t8",
    "temp_avg12in": "sv_t12",
    "temp_avg16in": "sv_t16",
    "temp_avg20in": "sv_t20",
    "temp_avg24in": "sv_t24",
    "temp_avg30in": "sv_t30",
    "temp_avg40in": "sv_t40",
}
VARCONV_TPOI4 = {
    "temp_avg4in": "t4_c_avg",
    "temp_avg12in": "t12_c_avg",
    "temp_avg24in": "t24_c_avg",
    "vwc_avg4in": "vwc4",
    "vwc_avg12in": "vwc12",
    "vwc_avg24in": "vwc24",
}

TSOIL_COLS = [
    "t4_c_avg",
    "t6_c_avg",
    "t12_c_avg",
    "t24_c_avg",
    "t50_c_avg",
]
BASE = "/home/loggernet"
STATIONS = {
    "CAMI4": "Calumet",
    "BOOI4": "AEAFarm",
    "WMNI4": "Wellman",
    "SBEI4": "Sibley",
    "NASI4": "Nashua",
    "OKLI4": "Lewis",
    "WTPI4": "WestPoint",
    "DONI4": "Doon",
    "KNAI4": "Kanawha",
    "GREI4": "Greenfield",
    "NWLI4": "Newell",
    "AEEI4": "Ames",
    "CNAI4": "Castana",
    "CHAI4": "Chariton",
    "CRFI4": "Crawfordsville",
    "FRUI4": "Muscatine",
    "CIRI4": "CedarRapids",
    "MCSI4": "Marcus",
    "AMFI4": "AmesFinch",
    # Temporary?
    # 'REFI4': 'Adel',
    # Vineyward
    "AHTI4": "AmesHort",
    "OSTI4": "TasselRidge",
    "BNKI4": "Bankston",
    "CSII4": "Inwood",
    "GVNI4": "Glenwood",
    "TPOI4": "Masonville",
    "DOCI4": "Jefferson",
}
INVERSION = {
    "BOOI4": "AEA",
}


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


def make_time(string):
    """Convert a time in the file to a datetime"""
    tstamp = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    tstamp = tstamp.replace(tzinfo=pytz.FixedOffset(-360))
    return tstamp


def do_inversion(filename, nwsli):
    """Process Inversion Station Data."""
    fn = f"{BASE}/{filename}_Inversion_MinSI.dat"
    if not os.path.isfile(fn):
        LOG.info("missing filename %s", fn)
        return
    df = pd.read_csv(fn, skiprows=[0, 2, 3], na_values=["NAN"])
    # convert all columns to lowercase
    df.columns = map(str.lower, df.columns)
    df["valid"] = df["timestamp"].apply(make_time)
    cursor = ISUAG.cursor()
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
    LOG.info("Inserted %s inversion rows for %s", len(df.index), nwsli)
    cursor.close()
    ISUAG.commit()


def common_df_logic(filename, maxts, nwsli, tablename):
    """Our commonality to reading"""
    if not os.path.isfile(filename):
        return

    df = pd.read_csv(filename, skiprows=[0, 2, 3], na_values=["NAN"])
    # convert all columns to lowercase
    df.columns = map(str.lower, df.columns)
    # rename columns to rectify differences
    df = df.rename(columns=VARCONV)
    # extra conversion for Deal's Orchard / Jefferson
    if nwsli == "DOCI4":
        df = df.rename(columns=VARCONV_JEFF)
    elif nwsli == "TPOI4":
        df = df.rename(columns=VARCONV_TPOI4)
    # QC out some bad temp values
    if tablename == "sm_daily" and nwsli in ["GVNI4", "CSII4"]:
        for col in ["tair_c_avg", "tair_c_min", "tair_c_max"]:
            df[col] = np.nan
    # rain_mm_tot to rain_in_tot
    for col in ["rain_mm_tot", "rain_mm_2_tot"]:
        if col in df.columns:
            df[col.replace("_mm_", "_in_")] = mm2inch(df[col])
    df = df.drop(
        [
            "rain_mm_tot",
            "rain_mm_2_tot",
            "pa06",
            "pa12",
            "pa24",
            "pa50",
            "rhnans_tot",
            "tairnans_tot",
            "winddir_sd1_wvt",
            "ec4",
        ],
        axis=1,
        errors="ignore",
    )
    if "ws_mps_s_wvt" in df.columns:
        df = df.assign(ws_mph=lambda df_: df_["ws_mps_s_wvt"] * 2.23694,).drop(
            columns=["ws_mps_s_wvt"],
        )

    if tablename == "sm_minute":
        # Storage of how far this covers
        df["duration"] = 15
        # slrkw_avg SIC is actually W/m2 over 15 minutes, we want to store as
        # a total over 15 minutes W/m2 -> kJ/s/m2
        df["slrkj_tot"] = df["slrkw_avg"] * 60.0 * 15.0 / 1000.0
        # drop our no longer needed columns
        df = df.drop(
            [
                "slrkw_avg",
                "slrmj_tot",
                "ws_mps_s_wvt",
                "ws_mph_tmx",
                "pa06",
                "pa12",
                "pa24",
                "pa50",
                "p06outofrange",
                "p12outofrange",
                "p24outofrange",
                "p50outofrange",
                "battv_min",
                "ec6",
                "ec12",
                "ec24",
                "ec50",
            ],
            axis=1,
            errors="ignore",
        )
        # HACK
        df = df.rename(
            columns={
                "calc_vwc_06_avg": "vwc6",
                "vwc_06_avg": "vwc6",
                "vwc_12_avg": "vwc12",
                "vwc_24_avg": "vwc24",
                "vwc_50_avg": "vwc50",
                "vwc_avg2in": "sv_vwc2",
                "vwc_avg4in": "sv_vwc4",
                "vwc_avg8in": "sv_vwc8",
                "vwc_avg12in": "sv_vwc12",
                "vwc_avg16in": "sv_vwc16",
                "vwc_avg20in": "sv_vwc20",
                "calc_vwc_12_avg": "vwc12",
                "calc_vwc_24_avg": "vwc24",
                "calc_vwc_50_avg": "vwc50",
                "bpres_avg": "bp_mb",
            }
        )
    df["valid"] = df["valid"].apply(make_time)
    # drop duplicate valids?
    df = df.groupby("valid").first().reset_index()
    if tablename == "sm_daily":
        # Horrible
        df = df.rename(
            columns={
                "calcvwc12_avg": "vwc12",
                "calcvwc24_avg": "vwc24",
            },
        )
        # Max wind speed
        if "ws_mps_max" in df.columns:
            df = (
                df.assign(
                    ws_mph_max=lambda df_: df_["ws_mps_max"] * 2.23694,
                )
                .drop(
                    columns=["ws_mps_max"],
                )
                .rename(
                    columns={"ws_mps_tmx": "ws_mph_tmx"},
                    errors="ignore",
                )
            )

        # Rework the valid column into the appropriate date
        df["valid"] = df["valid"].dt.date - datetime.timedelta(days=1)
        # Convert radiation to standardized slrkj_tot
        df["slrkj_tot"] = df["slrmj_tot"] * 1000.0
        # drop things we do not need
        df = df.drop(
            [
                "slrmj_tot",
                "solarradcalc",
                "nancounttot",
            ],
            axis=1,
            errors="ignore",
        )
    if tablename == "sm_hourly":
        # Horrible
        df = df.rename(
            columns={
                "calcvwc12_avg": "vwc12",
                "calcvwc24_avg": "vwc24",
            },
        )
        # Convert radiation to standardized slrkj_tot
        df["slrkj_tot"] = df["slrmj_tot"] * 1000.0
        # drop things we do not need
        df = df.drop(
            [
                "slrkw_avg",
                "solarradcalc",
                "slrmj_tot",
                "p06outofrange",
                "p12outofrange",
                "p24outofrange",
                "p50outofrange",
            ],
            axis=1,
            errors="ignore",
        )
    df = df[df["valid"] > maxts].copy()
    if df.empty:
        return

    df = df.drop("record", axis=1)
    # Create _qc and _f columns
    for colname in df.columns:
        if colname in ["valid", "duration"]:
            continue
        df[f"{colname}_qc"] = df[colname]
        if colname.startswith("vwc"):
            df[f"{colname}_f"] = qcval(df, f"{colname}_qc", 0.01, 0.7)
        elif colname in TSOIL_COLS:
            df[f"{colname}_f"] = qcval2(df, f"{colname}_qc", -20.0, 37.0)
        else:
            df[f"{colname}_f"] = None

    df["station"] = nwsli
    if "ws_mph_tmx" in df.columns:
        df["ws_mph_tmx"] = df["ws_mph_tmx"].apply(make_time)
    output = io.StringIO()
    df.to_csv(output, sep="\t", header=False, index=False)
    output.seek(0)
    icursor = ISUAG.cursor()
    try:
        icursor.copy_from(output, tablename, columns=df.columns, null="")
    except psycopg2.errors.UniqueViolation as exp:  # pylint: disable=no-member
        LOG.exception(exp)
        icursor.close()
        return
    icursor.close()
    ISUAG.commit()
    return df


def m15_process(nwsli, maxts):
    """Process the 15minute file"""
    fn = f"{BASE}/{STATIONS[nwsli]}_Min15SI.dat"
    df = common_df_logic(fn, maxts, nwsli, "sm_minute")
    if df is None:
        return 0

    # Update IEMAccess
    processed = 0
    LOG.info("processing %s rows from %s", len(df.index), fn)
    acursor = ACCESS.cursor()
    for _i, row in df.iterrows():
        ob = Observation(nwsli, "ISUSM", row["valid"].to_pydatetime())
        tmpc = units("degC") * row["tair_c_avg_qc"]
        tmpf = tmpc.to(units("degF")).m
        relh = units("percent") * row["rh_avg_qc"]
        if (-39 < tmpf < 140) and (0 < relh.m < 101):
            ob.data["tmpf"] = tmpf
            ob.data["relh"] = relh.m
            ob.data["dwpf"] = (
                dewpoint_from_relative_humidity(tmpc, relh).to(units("degF")).m
            )
        # ob.data["srad"] = row["slrkw_avg_qc"]
        ob.data["sknt"] = convert_value(
            row["ws_mph_qc"], "mile / hour", "knot"
        )
        ob.data["gust"] = convert_value(
            row["ws_mph_max_qc"], "mile / hour", "knot"
        )
        # ob.data["max_gust_ts"] = row["ws_mph_tmx"]
        ob.data["drct"] = row["winddir_d1_wvt_qc"]
        if "t4_c_avg" in df.columns:
            ob.data["c1tmpf"] = c2f(row["t4_c_avg_qc"])
        if "t12_c_avg" in df.columns:
            ob.data["c2tmpf"] = c2f(row["t12_c_avg_qc"])
        if "t24_c_avg" in df.columns:
            ob.data["c3tmpf"] = c2f(row["t24_c_avg_qc"])
        if "t50_c_avg" in df.columns:
            ob.data["c4tmpf"] = c2f(row["t50_c_avg_qc"])
        if "vwc12" in df.columns:
            ob.data["c2smv"] = row["vwc12_qc"] * 100.0
        if "vwc24" in df.columns:
            ob.data["c3smv"] = row["vwc24_qc"] * 100.0
        if "vwc50" in df.columns:
            ob.data["c4smv"] = row["vwc50_qc"] * 100.0
        ob.save(acursor, force_current_log=True)
        processed += 1
    acursor.close()
    ACCESS.commit()
    return processed


def hourly_process(nwsli, maxts):
    """Process the hourly file"""
    fn = f"{BASE}/{STATIONS[nwsli]}_HrlySI.dat"
    df = common_df_logic(fn, maxts, nwsli, "sm_hourly")
    if df is None:
        return 0
    processed = 0
    LOG.info("processing %s rows from %s", len(df.index), fn)
    acursor = ACCESS.cursor()
    for _i, row in df.iterrows():
        # Update IEMAccess
        ob = Observation(nwsli, "ISUSM", row["valid"].to_pydatetime())
        tmpc = units("degC") * row["tair_c_avg_qc"]
        tmpf = tmpc.to(units("degF")).m
        relh = units("percent") * row["rh_avg_qc"]
        if -40 < tmpf < 140 and 0 < relh.m < 101:
            ob.data["tmpf"] = tmpf
            ob.data["relh"] = relh.m
            ob.data["dwpf"] = (
                dewpoint_from_relative_humidity(tmpc, relh).to(units("degF")).m
            )
        ob.data["phour"] = round(row["rain_in_tot_qc"], 2)
        ob.data["sknt"] = convert_value(row["ws_mph"], "mile / hour", "knot")
        if "ws_mph_max" in df.columns:
            ob.data["gust"] = convert_value(
                row["ws_mph_max_qc"], "mile / hour", "knot"
            )
            ob.data["max_gust_ts"] = row["ws_mph_tmx"]
        ob.data["drct"] = row["winddir_d1_wvt_qc"]
        if "t4_c_avg" in df.columns:
            ob.data["c1tmpf"] = c2f(row["t4_c_avg_qc"])
        if "t12_c_avg_qc" in df.columns:
            ob.data["c2tmpf"] = c2f(row["t12_c_avg_qc"])
        if "t24_c_avg_qc" in df.columns:
            ob.data["c3tmpf"] = c2f(row["t24_c_avg_qc"])
        if "t50_c_avg" in df.columns:
            ob.data["c4tmpf"] = c2f(row["t50_c_avg_qc"])
        if "vwc12" in df.columns:
            ob.data["c2smv"] = row["vwc12_qc"] * 100.0
        if "vwc24" in df.columns:
            ob.data["c3smv"] = row["vwc24_qc"] * 100.0
        if "vwc50" in df.columns:
            ob.data["c4smv"] = row["vwc50_qc"] * 100.0
        ob.save(acursor)
        processed += 1
    acursor.close()
    ACCESS.commit()
    return processed


def daily_process(nwsli, maxts):
    """Process the daily file"""
    fn = f"{BASE}/{STATIONS[nwsli]}_DailySI.dat"
    df = common_df_logic(fn, maxts, nwsli, "sm_daily")
    if df is None:
        return 0
    LOG.info("processing %s rows from %s", len(df.index), fn)
    processed = 0
    acursor = ACCESS.cursor()
    for _i, row in df.iterrows():
        # Need a timezone
        valid = datetime.datetime(
            row["valid"].year, row["valid"].month, row["valid"].day, 12, 0
        )
        valid = valid.replace(tzinfo=pytz.timezone("America/Chicago"))
        ob = Observation(nwsli, "ISUSM", valid)
        ob.data["max_tmpf"] = c2f(row["tair_c_max_qc"])
        ob.data["min_tmpf"] = c2f(row["tair_c_min_qc"])
        ob.data["pday"] = round(row["rain_in_tot_qc"], 2)
        if valid not in EVENTS["days"]:
            EVENTS["days"].append(valid)
        ob.data["et_inch"] = mm2inch(row["dailyet_qc"])
        ob.data["srad_mj"] = row["slrkj_tot_qc"] / 1000.0
        # Someday check if this is apples to apples here
        ob.data["vector_avg_drct"] = row["winddir_d1_wvt_qc"]
        if ob.data["max_tmpf"] is None:
            EVENTS["reprocess_temps"] = True
        if ob.data["srad_mj"] == 0 or np.isnan(ob.data["srad_mj"]):
            LOG.info(
                "soilm_ingest.py station: %s ts: %s has 0 solar",
                nwsli,
                valid.strftime("%Y-%m-%d"),
            )
            EVENTS["reprocess_solar"] = True
        if "ws_mph_max_qc" in df.columns:
            ob.data["max_sknt"] = convert_value(
                row["ws_mph_max_qc"], "mile / hour", "knot"
            )
        ob.data["avg_sknt"] = convert_value(
            row["ws_mph_qc"], "mile / hour", "knot"
        )
        ob.save(acursor)

        processed += 1
    acursor.close()
    ACCESS.commit()
    return processed


def update_pday():
    """Compute today's precip from the current_log archive of data"""
    LOG.info("update_pday() called...")
    acursor = ACCESS.cursor()
    acursor.execute(
        """
        SELECT s.iemid, sum(case when phour > 0 then phour else 0 end) from
        current_log s JOIN stations t on (t.iemid = s.iemid)
        WHERE t.network = 'ISUSM' and valid > 'TODAY' GROUP by s.iemid
    """
    )
    data = {}
    for row in acursor:
        data[row[0]] = row[1]

    for iemid, entry in data.items():
        acursor.execute(
            "UPDATE summary SET pday = %s WHERE iemid = %s and day = 'TODAY'",
            (entry, iemid),
        )
    acursor.close()
    ACCESS.commit()


def get_max_timestamps(nwsli):
    """Fetch out our max values"""
    icursor = ISUAG.cursor()
    data = {
        "hourly": datetime.datetime(2012, 1, 1, tzinfo=pytz.FixedOffset(-360)),
        "minute": datetime.datetime(2012, 1, 1, tzinfo=pytz.FixedOffset(-360)),
        "daily": datetime.date(2012, 1, 1),
    }
    icursor.execute(
        """
        SELECT max(valid) from sm_daily
        WHERE station = %s
    """,
        (nwsli,),
    )
    row = icursor.fetchone()
    if row[0] is not None:
        data["daily"] = row[0]

    icursor.execute(
        """
        SELECT max(valid) from sm_hourly WHERE station = %s
    """,
        (nwsli,),
    )
    row = icursor.fetchone()
    if row[0] is not None:
        data["hourly"] = row[0]

    icursor.execute(
        """
        SELECT max(valid) from sm_minute
        WHERE station = %s
    """,
        (nwsli,),
    )
    row = icursor.fetchone()
    if row[0] is not None:
        data["minute"] = row[0]
    LOG.info(
        "%s max daily: %s hourly: %s minute: %s",
        nwsli,
        data["daily"],
        data["hourly"],
        data["minute"],
    )
    return data


def dump_raw_to_ldm(nwsli, dyprocessed, hrprocessed):
    """Send the raw datafile to LDM"""
    filename = f"{BASE}/{STATIONS[nwsli]}_DailySI.dat"
    if not os.path.isfile(filename):
        return
    fdata = open(filename, "rb").read().decode("ascii", "ignore")
    lines = fdata.split("\n")
    if len(lines) < 5:
        return

    tmpfd, tmpfn = tempfile.mkstemp()
    os.write(tmpfd, lines[0].encode("ascii", "ignore"))
    os.write(tmpfd, lines[1].encode("ascii", "ignore"))
    os.write(tmpfd, lines[2].encode("ascii", "ignore"))
    os.write(tmpfd, lines[3].encode("ascii", "ignore"))
    for linenum in range(0 - dyprocessed, 0):
        os.write(tmpfd, lines[linenum].encode("ascii", "ignore"))
    os.close(tmpfd)
    cmd = (
        "pqinsert -p "
        f"'data c {utc():%Y%m%d%H%M} csv/isusm/{nwsli}_daily.txt bogus txt' "
        f"{tmpfn}"
    )
    proc = subprocess.Popen(
        cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    proc.stdout.read()
    os.remove(tmpfn)

    # Send the raw datafile to LDM
    filename = f"{BASE}/{STATIONS[nwsli]}_HrlySI.dat"
    if not os.path.isfile(filename):
        return
    # Sometimes this file has corrupted characters?
    fdata = open(filename, "rb").read().decode("ascii", "ignore")
    lines = fdata.split("\n")
    if len(lines) < 5:
        return

    tmpfd, tmpfn = tempfile.mkstemp()
    os.write(tmpfd, lines[0].encode("ascii", "ignore"))
    os.write(tmpfd, lines[1].encode("ascii", "ignore"))
    os.write(tmpfd, lines[2].encode("ascii", "ignore"))
    os.write(tmpfd, lines[3].encode("ascii", "ignore"))
    for linenum in range(0 - hrprocessed, 0):
        os.write(tmpfd, lines[linenum].encode("ascii", "ignore"))
    os.close(tmpfd)
    cmd = (
        "pqinsert -p "
        f"'data c {utc():%Y%m%d%H%M} csv/isusm/{nwsli}_hourly.txt bogus txt' "
        f"{tmpfn}"
    )
    proc = subprocess.Popen(
        cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    proc.stdout.read()
    os.remove(tmpfn)


def main(argv):
    """Go main Go"""
    stations = STATIONS if len(argv) == 1 else [argv[1]]
    for nwsli in stations:
        LOG.info("starting workflow for: %s", nwsli)
        maxobs = get_max_timestamps(nwsli)
        m15processed = m15_process(nwsli, maxobs["minute"])
        hrprocessed = hourly_process(nwsli, maxobs["hourly"])
        dyprocessed = daily_process(nwsli, maxobs["daily"])
        if hrprocessed > 0:
            dump_raw_to_ldm(nwsli, dyprocessed, hrprocessed)
        LOG.info(
            "%s 15min:%s hr:%s daily:%s",
            nwsli,
            m15processed,
            hrprocessed,
            dyprocessed,
        )
    update_pday()
    for nwsli, item in INVERSION.items():
        do_inversion(item, nwsli)

    if EVENTS["reprocess_solar"]:
        LOG.info("Calling fix_solar.py with no args")
        subprocess.call("python ../isuag/fix_solar.py", shell=True)
    if EVENTS["reprocess_temps"]:
        LOG.info("Calling fix_temps.py with no args")
        subprocess.call("python ../isuag/fix_temps.py", shell=True)
    for day in EVENTS["days"]:
        LOG.info("Calling fix_{solar,precip}.py for %s", day)
        subprocess.call(
            f"python ../isusm/fix_precip.py {day:%Y %m %d}",
            shell=True,
        )
        subprocess.call(
            f"python ../isuag/fix_solar.py {day:%Y %m %d}",
            shell=True,
        )


def test_make_tstamp():
    """Do we do the right thing with timestamps"""
    res = make_time("2017-08-31 19:00:00")
    assert res.strftime("%H") == "19"


if __name__ == "__main__":
    main(sys.argv)
