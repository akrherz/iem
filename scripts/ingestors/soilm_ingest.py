"""
    LEGACY ISU SOIL MOISTURE INGEST!

 Run from RUN_10_AFTER.sh
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
from pyiem.util import get_dbconn, logger, convert_value, c2f, mm2inch

LOG = logger()
ISUAG = get_dbconn("isuag")

ACCESS = get_dbconn("iem")

EVENTS = {"reprocess_solar": False, "days": [], "reprocess_temps": False}
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
    "outofrange06": "p06outofrange",
    "outofrange12": "p12outofrange",
    "outofrange24": "p24outofrange",
    "outofrange50": "p50outofrange",
    "ws_ms_s_wvt": "ws_mps_s_wvt",
    "ec6in": "ec06",
    "ec12in": "ec12",
    "ec_24in": "ec24",
    "ec24in": "ec24",
    "temp_avg6in": "t06_c_avg",
    "temp_avg12in": "t12_c_avg",
    "temp_avg24in": "t24_c_avg",
    "bp_mmhg_avg": "bpres_avg",
    "bp_mb_avg": "bpres_avg",
}

TSOIL_COLS = [
    "tsoil_c_avg",
    "t06_c_avg",
    "t12_c_avg",
    "t24_c_avg",
    "t50_c_avg",
]
BASE = "/mnt/home/loggernet"
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


def common_df_logic(filename, maxts, nwsli, tablename):
    """Our commonality to reading"""
    if not os.path.isfile(filename):
        return

    df = pd.read_csv(filename, skiprows=[0, 2, 3], na_values=["NAN"])
    # convert all columns to lowercase
    df.columns = map(str.lower, df.columns)
    # rename columns to rectify differences
    df.rename(columns=VARCONV, inplace=True)
    if tablename == "sm_minute":
        # Storage of how far this covers
        df["duration"] = 15
        # Some conversions needed to map this data back to 1min table
        # slrkw_avg SIC is actually W/m2 over 15 minutes, we want to store as
        # a total over "one minute" W/m2 -> kJ/s/m2
        df["slrkj_tot"] = df["slrkw_avg"] * 60.0 / 1000.0
        # rain_mm_tot to rain_in_tot
        df["rain_in_tot"] = df["rain_mm_tot"] / 25.4
        if "rain_mm_2_tot" in df.columns:
            df["rain_in_2_tot"] = df["rain_mm_2_tot"] / 25.4
            df = df.drop("rain_mm_2_tot", axis=1)
        # Wind
        df["ws_mph_s_wvt"] = df["ws_mps_s_wvt"] * 2.23694
        # drop our no longer needed columns
        df = df.drop(
            [
                "slrkw_avg",
                "slrmj_tot",
                "rain_mm_tot",
                "ws_mps_s_wvt",
                "winddir_sd1_wvt",
                "ws_mph_tmx",
                "ec06",
                "ec12",
                "ec24",
                "ec50",
                "pa06",
                "pa12",
                "pa24",
                "pa50",
                "p06outofrange",
                "p12outofrange",
                "p24outofrange",
                "p50outofrange",
                "battv_min",
                "ec_2in",
                "ec_4in",
                "ec_8in",
                "ec_12in",
                "ec_16in",
                "ec_20in",
            ],
            axis=1,
            errors="ignore",
        )
        # HACK
        df = df.rename(
            columns={
                "calc_vwc_06_avg": "calcvwc06_avg",
                "vwc_06_avg": "calcvwc06_avg",
                "vwc_12_avg": "calcvwc12_avg",
                "vwc_24_avg": "calcvwc24_avg",
                "vwc_50_avg": "calcvwc50_avg",
                "vwc_avg2in": "calcvwc02_avg",
                "vwc_avg4in": "calcvwc04_avg",
                "vwc_avg8in": "calcvwc08_avg",
                "vwc_avg12in": "calcvwc12_avg",
                "vwc_avg16in": "calcvwc16_avg",
                "vwc_avg20in": "calcvwc20_avg",
                "calc_vwc_12_avg": "calcvwc12_avg",
                "calc_vwc_24_avg": "calcvwc24_avg",
                "calc_vwc_50_avg": "calcvwc50_avg",
                "temp_avg2in": "t02_c_avg",
                "temp_avg4in": "t04_c_avg",
                "temp_avg8in": "t08_c_avg",
                "temp_avg12in": "t12_c_avg",
                "temp_avg16in": "t16_c_avg",
                "temp_avg20in": "t20_c_avg",
                "bpres_avg": "bp_mb",
                "rh": "rh_avg",
            }
        )
    df["valid"] = df["valid"].apply(make_time)
    if tablename == "sm_daily":
        # Rework the valid column into the appropriate date
        df["valid"] = df["valid"].dt.date - datetime.timedelta(days=1)
        # Convert radiation to standardized slrkj_tot
        df["slrkj_tot"] = df["slrmj_tot"] * 1000.0
        # drop things we do not need
        df = df.drop(
            [
                "slrmj_tot",
                "solarradcalc",
            ],
            axis=1,
            errors="ignore",
        )
    if tablename == "sm_hourly":
        # Convert radiation to standardized slrkj_tot
        df["slrkj_tot"] = df["slrmj_tot"] * 1000.0
        # drop things we do not need
        df = df.drop(
            [
                "slrkw_avg",
                "solarradcalc",
                "slrmj_tot",
            ],
            axis=1,
            errors="ignore",
        )
    df = df[df["valid"] > maxts].copy()
    if df.empty:
        return

    df.drop("record", axis=1, inplace=True)
    # Create _qc and _f columns
    for colname in df.columns:
        if colname in ["valid", "duration"]:
            continue
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
    fn = "%s/%s_Min15SI.dat" % (BASE, STATIONS[nwsli])
    df = common_df_logic(fn, maxts, nwsli, "sm_minute")
    if df is None:
        return 0

    # Update IEMAccess
    processed = 0
    LOG.debug("processing %s rows from %s", len(df.index), fn)
    acursor = ACCESS.cursor()
    for _i, row in df.iterrows():
        ob = Observation(nwsli, "ISUSM", row["valid"].to_pydatetime())
        tmpc = units("degC") * row["tair_c_avg_qc"]
        tmpf = tmpc.to(units("degF")).m
        relh = units("percent") * row["rh_avg_qc"]
        if (-39 < tmpf < 140) and (0 < relh < 101):
            ob.data["tmpf"] = tmpf
            ob.data["relh"] = relh.m
            ob.data["dwpf"] = (
                dewpoint_from_relative_humidity(tmpc, relh).to(units("degF")).m
            )
        # ob.data["srad"] = row["slrkw_avg_qc"]
        ob.data["sknt"] = convert_value(
            row["ws_mph_s_wvt_qc"], "mile / hour", "knot"
        )
        ob.data["gust"] = convert_value(
            row["ws_mph_max_qc"], "mile / hour", "knot"
        )
        # ob.data["max_gust_ts"] = row["ws_mph_tmx"]
        ob.data["drct"] = row["winddir_d1_wvt_qc"]
        if "tsoil_c_avg" in df.columns:
            ob.data["c1tmpf"] = c2f(row["tsoil_c_avg_qc"])
        if "t12_c_avg" in df.columns:
            ob.data["c2tmpf"] = c2f(row["t12_c_avg_qc"])
        if "t24_c_avg" in df.columns:
            ob.data["c3tmpf"] = c2f(row["t24_c_avg_qc"])
        if "t50_c_avg" in df.columns:
            ob.data["c4tmpf"] = c2f(row["t50_c_avg_qc"])
        if "calc_vwc_12_avg" in df.columns:
            ob.data["c2smv"] = row["calc_vwc_12_avg_qc"] * 100.0
        if "calc_vwc_24_avg" in df.columns:
            ob.data["c3smv"] = row["calc_vwc_24_avg_qc"] * 100.0
        if "calc_vwc_50_avg" in df.columns:
            ob.data["c4smv"] = row["calc_vwc_50_avg_qc"] * 100.0
        ob.save(acursor, force_current_log=True)
        processed += 1
    acursor.close()
    ACCESS.commit()
    return processed


def hourly_process(nwsli, maxts):
    """Process the hourly file"""
    fn = "%s/%s_HrlySI.dat" % (BASE, STATIONS[nwsli])
    df = common_df_logic(fn, maxts, nwsli, "sm_hourly")
    if df is None:
        return 0
    processed = 0
    LOG.debug("processing %s rows from %s", len(df.index), fn)
    acursor = ACCESS.cursor()
    for _i, row in df.iterrows():
        # Update IEMAccess
        ob = Observation(nwsli, "ISUSM", row["valid"].to_pydatetime())
        tmpc = units("degC") * row["tair_c_avg_qc"]
        tmpf = tmpc.to(units("degF")).m
        relh = units("percent") * row["rh_qc"]
        if -40 < tmpf < 140 and 0 < relh < 101:
            ob.data["tmpf"] = tmpf
            ob.data["relh"] = relh.m
            ob.data["dwpf"] = (
                dewpoint_from_relative_humidity(tmpc, relh).to(units("degF")).m
            )
        ob.data["phour"] = round(mm2inch(row["rain_mm_tot_qc"]), 2)
        ob.data["sknt"] = convert_value(
            row["ws_mps_s_wvt_qc"], "meter / second", "knot"
        )
        if "ws_mph_max" in df.columns:
            ob.data["gust"] = convert_value(
                row["ws_mph_max_qc"], "mile / hour", "knot"
            )
            ob.data["max_gust_ts"] = row["ws_mph_tmx"]
        ob.data["drct"] = row["winddir_d1_wvt_qc"]
        if "tsoil_c_avg" in df.columns:
            ob.data["c1tmpf"] = c2f(row["tsoil_c_avg_qc"])
        if "t12_c_avg_qc" in df.columns:
            ob.data["c2tmpf"] = c2f(row["t12_c_avg_qc"])
        if "t24_c_avg_qc" in df.columns:
            ob.data["c3tmpf"] = c2f(row["t24_c_avg_qc"])
        if "t50_c_avg" in df.columns:
            ob.data["c4tmpf"] = c2f(row["t50_c_avg_qc"])
        if "calc_vwc_12_avg" in df.columns:
            ob.data["c2smv"] = row["calc_vwc_12_avg_qc"] * 100.0
        if "calc_vwc_24_avg" in df.columns:
            ob.data["c3smv"] = row["calc_vwc_24_avg_qc"] * 100.0
        if "calc_vwc_50_avg" in df.columns:
            ob.data["c4smv"] = row["calc_vwc_50_avg_qc"] * 100.0
        ob.save(acursor)
        processed += 1
    acursor.close()
    ACCESS.commit()
    return processed


def daily_process(nwsli, maxts):
    """Process the daily file"""
    fn = "%s/%s_DailySI.dat" % (BASE, STATIONS[nwsli])
    df = common_df_logic(fn, maxts, nwsli, "sm_daily")
    if df is None:
        return 0
    LOG.debug("processing %s rows from %s", len(df.index), fn)
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
        ob.data["pday"] = round(mm2inch(row["rain_mm_tot_qc"]), 2)
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
        if "ws_mps_max" in df.columns:
            ob.data["max_sknt"] = convert_value(
                row["ws_mps_max_qc"], "meter / second", "knot"
            )
        ob.data["avg_sknt"] = convert_value(
            row["ws_mps_s_wvt_qc"], "meter / second", "knot"
        )
        ob.save(acursor)

        processed += 1
    acursor.close()
    ACCESS.commit()
    return processed


def update_pday():
    """Compute today's precip from the current_log archive of data"""
    LOG.debug("update_pday() called...")
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

    for iemid in data:
        acursor.execute(
            """
            UPDATE summary SET pday = %s
            WHERE iemid = %s and day = 'TODAY'
        """,
            (data[iemid], iemid),
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
    LOG.debug(
        "%s max daily: %s hourly: %s minute: %s",
        nwsli,
        data["daily"],
        data["hourly"],
        data["minute"],
    )
    return data


def dump_raw_to_ldm(nwsli, dyprocessed, hrprocessed):
    """Send the raw datafile to LDM"""
    filename = "%s/%s_DailySI.dat" % (BASE, STATIONS[nwsli])
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
        "pqinsert -p " "'data c %s csv/isusm/%s_daily.txt bogus txt' %s"
    ) % (datetime.datetime.utcnow().strftime("%Y%m%d%H%M"), nwsli, tmpfn)
    proc = subprocess.Popen(
        cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    proc.stdout.read()
    os.remove(tmpfn)

    # Send the raw datafile to LDM
    filename = "%s/%s_HrlySI.dat" % (BASE, STATIONS[nwsli])
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
        "pqinsert -p " "'data c %s csv/isusm/%s_hourly.txt bogus txt' %s"
    ) % (datetime.datetime.utcnow().strftime("%Y%m%d%H%M"), nwsli, tmpfn)
    proc = subprocess.Popen(
        cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    proc.stdout.read()
    os.remove(tmpfn)


def main(argv):
    """Go main Go"""
    stations = STATIONS if len(argv) == 1 else [argv[1]]
    for nwsli in stations:
        LOG.debug("starting workflow for: %s", nwsli)
        maxobs = get_max_timestamps(nwsli)
        m15processed = m15_process(nwsli, maxobs["minute"])
        hrprocessed = hourly_process(nwsli, maxobs["hourly"])
        dyprocessed = daily_process(nwsli, maxobs["daily"])
        if hrprocessed > 0:
            dump_raw_to_ldm(nwsli, dyprocessed, hrprocessed)
        LOG.debug(
            "%s 15min:%s hr:%s daily:%s",
            nwsli,
            m15processed,
            hrprocessed,
            dyprocessed,
        )
    update_pday()

    if EVENTS["reprocess_solar"]:
        LOG.info("Calling fix_solar.py with no args")
        subprocess.call("python ../isuag/fix_solar.py", shell=True)
    if EVENTS["reprocess_temps"]:
        LOG.info("Calling fix_temps.py with no args")
        subprocess.call("python ../isuag/fix_temps.py", shell=True)
    for day in EVENTS["days"]:
        LOG.info("Calling fix_{solar,precip}.py for %s", day)
        subprocess.call(
            ("python ../isusm/fix_precip.py %s %s %s")
            % (day.year, day.month, day.day),
            shell=True,
        )
        subprocess.call(
            ("python ../isuag/fix_solar.py %s %s %s")
            % (day.year, day.month, day.day),
            shell=True,
        )


def test_make_tstamp():
    """Do we do the right thing with timestamps"""
    res = make_time("2017-08-31 19:00:00")
    assert res.strftime("%H") == "19"


if __name__ == "__main__":
    main(sys.argv)
