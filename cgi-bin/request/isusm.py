"""Download interface for ISU-SM data."""
import datetime
from io import BytesIO, StringIO

import numpy as np
import pandas as pd
from paste.request import parse_formvars
from pyiem.util import convert_value, get_sqlalchemy_conn
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MISSING = {"", "M", "-99"}
SV_DEPTHS = [2, 4, 8, 12, 14, 16, 20, 24, 28, 30, 32, 36, 40, 42, 52]


def get_stations(form):
    """Figure out which stations were requested"""
    stations = form.getall("sts")
    if not stations:
        stations.append("XXXXX")
    if len(stations) == 1:
        stations.append("XXXXX")
    return stations


def get_dates(form):
    """Get the start and end dates requested"""
    year1 = form.get("year1", 2013)
    month1 = form.get("month1", 1)
    day1 = form.get("day1", 1)
    year2 = form.get("year2", 2013)
    month2 = form.get("month2", 1)
    day2 = form.get("day2", 1)

    try:
        sts = datetime.datetime(int(year1), int(month1), int(day1))
        ets = datetime.datetime(int(year2), int(month2), int(day2))
    except Exception:
        return None, None

    if sts > ets:
        sts, ets = ets, sts
    if sts == ets:
        ets = sts + datetime.timedelta(days=1)
    return sts, ets


def get_delimiter(form):
    """Figure out what is the requested delimiter"""
    d = form.getvalue("delim", "comma")
    if d == "comma":
        return ","
    return "\t"


def fetch_daily(form, cols):
    """Return a fetching of daily data"""
    sts, ets = get_dates(form)
    if sts is None:
        return None, []
    stations = get_stations(form)

    if not cols:
        cols = [
            "station",
            "valid",
            "high",
            "low",
            "rh_min",
            "rh",
            "rh_max",
            "gdd50",
            "solar",
            "precip",
            "speed",
            "gust",
            "et",
            "soil04t",
            "soil12t",
            "soil24t",
            "soil50t",
            "soil12vwc",
            "soil24vwc",
            "soil50vwc",
        ]
    else:
        cols.insert(0, "valid")
        cols.insert(0, "station")
    if "sv" in cols:
        # SoilVue 10 data
        for depth in SV_DEPTHS:
            for c2 in ["t", "vwc"]:
                cols.append(f"sv_{c2}{depth}")

    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            text(
                """
    --- Get the Daily Max/Min soil values
    WITH soils as (
      SELECT station, date(valid) as date,
      min(rh_avg_qc) as rh_min,
      avg(rh_avg_qc) as rh,
      max(rh_avg_qc) as rh_max,
      min(t12_c_avg_qc) as soil12tn, max(t12_c_avg_qc) as soil12tx,
      min(t24_c_avg_qc) as soil24tn, max(t24_c_avg_qc) as soil24tx,
      min(t50_c_avg_qc) as soil50tn, max(t50_c_avg_qc) as soil50tx
      from sm_hourly where
      valid >= :sts and valid < :ets and station in :stations
      GROUP by station, date
    ), daily as (
      SELECT *,
      t4_c_min_qc as soil04tn, t4_c_max_qc as soil04tx,
      round(gddxx(50, 86, c2f( tair_c_max_qc ),
        c2f( tair_c_min_qc ))::numeric,1) as gdd50 from sm_daily WHERE
      valid >= :sts and valid < :ets and station in :stations
    )
    SELECT d.*, s.rh_min, s.rh, s.rh_max, s.soil04tn, s.soil04tx,
    s.soil12tn, s.soil12tx, s.soil24tn, s.soil24tx, s.soil50tn, s.soil50tx
    FROM soils s JOIN daily d on (d.station = s.station and s.date = d.valid)
    ORDER by d.valid ASC
    """
            ),
            conn,
            params={
                "sts": sts,
                "ets": ets,
                "stations": tuple(stations),
            },
            index_col=None,
        )

    if df.empty:
        return df, []

    df = df.fillna(np.nan)

    # Direct copy / rename
    xref = {
        "rh_avg_qc": "relh",
        "rain_in_tot_qc": "precip",
        "winddir_d1_wvt_qc": "drct",
        "vwc12_qc": "soil12vwc",
        "vwc24_qc": "soil24vwc",
        "vwc50_qc": "soil50vwc",
        "dailyet_qc": "et",
    }
    df = df.rename(columns=xref, errors="ignore")
    # Mul by 100 for %
    for depth in [12, 24, 50]:
        df[f"soil{depth}vwc"] = df[f"soil{depth}vwc"] * 100.0
    # Now we need to do some mass data conversion, sigh
    tc = {
        "high": "tair_c_max_qc",
        "low": "tair_c_min_qc",
        "soil04t": "t4_c_avg_qc",
        "soil04tn": "soil04tn",
        "soil04tx": "soil04tx",
        "soil12t": "t12_c_avg_qc",
        "soil12tn": "soil12tn",
        "soil12tx": "soil12tx",
        "soil24t": "t24_c_avg_qc",
        "soil24tn": "soil24tn",
        "soil24tx": "soil24tx",
        "soil50t": "t50_c_avg_qc",
        "soil50tn": "soil50tn",
        "soil50tx": "soil50tx",
    }
    for key, col in tc.items():
        if key not in cols:
            continue
        # Do the work
        df[key] = convert_value(df[col].values, "degC", "degF")

    if "speed" in cols:
        df = df.rename(columns={"ws_mph_qc": "speed"})
    if "gust" in cols:
        df = df.rename(columns={"ws_mph_max_qc": "gust"})
    if "sv" in cols:
        # SoilVue 10 data
        for depth in SV_DEPTHS:
            df[f"sv_t{depth}"] = convert_value(
                df[f"sv_t{depth}_qc"].values, "degC", "degF"
            )
            # Copy
            df[f"sv_vwc{depth}"] = df[f"sv_vwc{depth}_qc"]
        # Remove the original
        cols.remove("sv")

    # Convert solar radiation to J/m2
    if "solar" in cols:
        df["solar"] = df["slrkj_tot_qc"] * 1000.0
    if "solar_mj" in cols:
        df["solar_mj"] = df["slrkj_tot_qc"] / 1000.0
    if "et" in cols:
        df["et"] = convert_value(df["et"], "mm", "inch")

    overwrite = (
        "bp_mb lwmv_1 lwmv_2 lwmdry_1_tot lwmcon_1_tot lwmwet_1_tot "
        "lwmdry_2_tot lwmcon_2_tot lwmwet_2_tot bpres_avg"
    ).split()
    for col in overwrite:
        if col in cols:
            # Overwrite
            df[col] = df[f"{col}_qc"]

    return df, cols


def fetch_hourly(form, cols):
    """Process the request for hourly/minute data."""
    sts, ets = get_dates(form)
    if sts is None:
        return None, []
    stations = get_stations(form)

    if not cols:
        cols = [
            "station",
            "valid",
            "tmpf",
            "relh",
            "solar",
            "precip",
            "speed",
            "drct",
            "et",
            "soil04t",
            "soil12t",
            "soil24t",
            "soil50t",
            "soil12vwc",
            "soil24vwc",
            "soil50vwc",
        ]
    else:
        cols.insert(0, "valid")
        cols.insert(0, "station")

    table = "sm_hourly"
    sqlextra = ", null as bp_mb_qc "
    if form.get("timeres") == "minute":
        table = "sm_minute"
        sqlextra = ", null as etalfalfa_qc"
    if "sv" in cols:
        # SoilVue 10 data
        for depth in SV_DEPTHS:
            for c2 in ["t", "vwc"]:
                cols.append(f"sv_{c2}{depth}")
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            text(
                "SELECT *, valid at time zone 'UTC' as utc_valid "
                f"{sqlextra} from {table} WHERE valid >= :sts "
                "and valid < :ets and station in :stations ORDER by valid ASC"
            ),
            conn,
            params={
                "sts": sts,
                "ets": ets,
                "stations": tuple(stations),
            },
            index_col=None,
        )
    if df.empty:
        return df, cols

    # Muck with the timestamp column
    if form.get("tz") == "utc":
        df["valid"] = df["utc_valid"].dt.strftime("%Y-%m-%d %H:%M+00")
    else:
        df["valid"] = (
            df["utc_valid"]
            .dt.tz_localize("UTC")
            .dt.tz_convert("US/Central")
            .dt.strftime("%Y-%m-%d %H:%M")
        )

    df = df.fillna(np.nan)
    # Direct copy / rename
    xref = {
        "rh_avg_qc": "relh",
        "rain_in_tot_qc": "precip",
        "winddir_d1_wvt_qc": "drct",
        "vwc12_qc": "soil12vwc",
        "vwc24_qc": "soil24vwc",
        "vwc50_qc": "soil50vwc",
    }
    df = df.rename(columns=xref, errors="ignore")
    # Mul by 100 for %
    for depth in [12, 24, 50]:
        df[f"soil{depth}vwc"] = df[f"soil{depth}vwc"] * 100.0
    # Now we need to do some mass data conversion, sigh
    tc = {
        "tmpf": "tair_c_avg_qc",
        "soil04t": "t4_c_avg_qc",
        "soil12t": "t12_c_avg_qc",
        "soil24t": "t24_c_avg_qc",
        "soil50t": "t50_c_avg_qc",
    }
    for key, col in tc.items():
        if key not in cols:
            continue
        # Do the work
        df[key] = convert_value(df[col].values, "degC", "degF")

    if "sv" in cols:
        # SoilVue 10 data
        for depth in SV_DEPTHS:
            df[f"sv_t{depth}"] = convert_value(
                df[f"sv_t{depth}_qc"].values, "degC", "degF"
            )
            # Copy
            df[f"sv_vwc{depth}"] = df[f"sv_vwc{depth}_qc"]
        # Remove the original
        cols.remove("sv")

    # Convert solar radiation to J/m2
    if "solar" in cols:
        df["solar"] = df["slrkj_tot_qc"] * 1000.0

    if "speed" in cols:
        df["speed"] = df["ws_mph_qc"]

    if "et" in cols:
        df["et"] = convert_value(df["etalfalfa_qc"].values, "mm", "inch")

    overwrite = (
        "bp_mb lwmv_1 lwmv_2 lwmdry_1_tot lwmcon_1_tot lwmwet_1_tot "
        "lwmdry_2_tot lwmcon_2_tot lwmwet_2_tot bpres_avg"
    ).split()
    for col in overwrite:
        if col in cols:
            # Overwrite
            df[col] = df[f"{col}_qc"]

    return df, cols


def application(environ, start_response):
    """Do things"""
    form = parse_formvars(environ)
    mode = form.get("mode", "hourly")
    cols = form.getall("vars")
    fmt = form.get("format", "csv").lower()
    todisk = form.get("todisk", "no")
    if mode == "hourly":
        df, cols = fetch_hourly(form, cols)
    else:
        df, cols = fetch_daily(form, cols)

    if df is None or df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"Sorry, no data found for this query."]

    miss = form.get("missing", "-99")
    assert miss in MISSING
    df = df.replace({np.nan: miss})

    if fmt == "excel":
        bio = BytesIO()
        # pylint: disable=abstract-class-instantiated
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, "Data", columns=cols, index=False)
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", "attachment; Filename=isusm.xlsx"),
        ]
        start_response("200 OK", headers)
        return [bio.getvalue()]

    delim = "," if fmt == "comma" else "\t"
    sio = StringIO()
    df.to_csv(sio, index=False, columns=cols, sep=delim)

    if todisk == "yes":
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", "attachment; filename=isusm.txt"),
        ]
    else:
        headers = [("Content-type", "text/plain")]
    start_response("200 OK", headers)
    return [sio.getvalue().encode("ascii")]
