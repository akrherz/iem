""".. title:: ISU Soil Moisture Data Download Service

This service emits data from the ISU Soil Moisture Network.

Changelog
---------

- 2025-01-27: Added support for `qcflags` for the inclusion of the flag
  values.
- **2024-11-19** Initial update to use pydantic request validation.

Example Requests
----------------

Provide an Excel file of the minute data for the Hinds Farm station on
21 July 2024.

https://mesonet.agron.iastate.edu/cgi-bin/request/isusm.py?station=AHDI4&\
mode=hourly&sts=2024-07-21T05:00Z&ets=2024-07-22T05:00Z&format=excel&\
timeres=minute

Provide all of the daily data for the Hinds Farm station for the month of
July 2024 in a tab delimited format.

https://mesonet.agron.iastate.edu/cgi-bin/request/isusm.py?station=AHDI4&\
mode=daily&sts=2024-07-01T00:00Z&ets=2024-08-01T00:00Z&format=tab

Provide all of the hourly data for the Hinds Farm station for the month of
July 2024 in a comma delimited format with timestampts in UTC and include
any QC flags.  Also include the SoilVue 10 data.

https://mesonet.agron.iastate.edu/cgi-bin/request/isusm.py?station=AHDI4&\
mode=hourly&sts=2024-07-01T00:00Z&ets=2024-08-01T00:00Z&format=comma&tz=UTC\
&qcflags=1&vars=sv

Same as the last, but for daily data this time and solar radiation in MJ/m2

https://mesonet.agron.iastate.edu/cgi-bin/request/isusm.py?station=AHDI4&\
mode=daily&sts=2024-07-01T00:00Z&ets=2024-08-01T00:00Z&format=comma&tz=UTC\
&qcflags=1&vars=sv,solar_mj

"""

import re
import warnings
from datetime import timedelta
from io import BytesIO, StringIO
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from pydantic import AwareDatetime, Field, field_validator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import convert_value
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

# Cull a fragmentation warning from pandas due to our hacky things
warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

pd.set_option("future.no_silent_downcasting", True)
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
LEGACY_STS = re.compile("sts=[A-Z]")
MISSING = {"", "M", "-99"}
SV_DEPTHS = [2, 4, 8, 12, 14, 16, 20, 24, 28, 30, 32, 36, 40, 42, 52]
DELIMITERS = {"comma": ",", "tab": "\t"}


class Schema(CGIModel):
    """See how we are called..."""

    chillbase: float = Field(
        default=32, description="Chill Hours Base Temperature [degF]"
    )
    chillceil: float = Field(
        default=45, description="Chill Hours Ceiling Temperature [degF]"
    )
    delim: str = Field(
        description="Delimiter", default="comma", pattern="comma|tab"
    )
    ets: AwareDatetime = Field(default=None, description="End Time")
    format: str = Field(
        default="csv",
        description="Output Format",
        pattern="csv|comma|excel|tab",
    )
    missing: str = Field(
        default="-99",
        description="Missing Value Indicator",
        pattern="^-99|M|$",
    )
    qcflags: bool = Field(
        default=False,
        description="Include QC Flag Values",
    )
    sts: AwareDatetime = Field(default=None, description="Start Time")
    mode: str = Field(
        default="hourly",
        description="Data Mode",
        pattern="hourly|daily|inversion",
    )
    station: ListOrCSVType = Field(description="Station Identifier(s)")
    timeres: str = Field(
        default="hourly",
        description="Time Resolution for hourly request",
        pattern="hourly|minute",
    )
    todisk: str = Field(
        default="no", description="Download to Disk", pattern="yes|no"
    )
    tz: str = Field(
        default="America/Chicago",
        description="Timezone for output",
    )
    vars: ListOrCSVType = Field(
        default=None, description="Variables to include in output"
    )
    year1: int = Field(
        default=None, description="Start year if sts is not provided"
    )
    month1: int = Field(
        default=None, description="Start month if sts is not provided"
    )
    day1: int = Field(
        default=None, description="Start day if sts is not provided"
    )
    hour1: int = Field(
        default=0, description="Start hour if sts is not provided"
    )
    minute1: int = Field(
        default=0, description="Start minute if sts is not provided"
    )
    year2: int = Field(
        default=None, description="End year if ets is not provided"
    )
    month2: int = Field(
        default=None, description="End month if ets is not provided"
    )
    day2: int = Field(
        default=None, description="End day if ets is not provided"
    )
    hour2: int = Field(
        default=0, description="End hour if ets is not provided"
    )
    minute2: int = Field(
        default=0, description="End minute if ets is not provided"
    )

    @field_validator("tz", mode="after")
    @classmethod
    def check_tz(cls, value):
        """Ensure the timezone is valid."""
        ZoneInfo(value)
        return value


def fetch_daily(environ: dict, cols: list):
    """Return a fetching of daily data"""
    stations: list = environ["station"]

    if not cols:
        cols = (
            "station valid high low rh_min rh rh_max gdd50 solar precip "
            "speed gust et soil04t soil12t soil24t soil50t soil12vwc "
            "soil24vwc soil50vwc"
        ).split()
    else:
        cols.insert(0, "valid")
        cols.insert(0, "station")
    if environ["qcflags"]:
        newcols = cols[:2]
        for col in cols[2:]:
            newcols.extend([col, f"{col}_f"])
        cols = newcols

    if "sv" in cols:
        # SoilVue 10 data
        for depth in SV_DEPTHS:
            for c2 in ["t", "vwc"]:
                cols.append(f"sv_{c2}{depth}")
                if environ["qcflags"]:
                    cols.append(f"sv_{c2}{depth}_f")
    else:
        for col in list(cols):
            if col.startswith("sv") and len(col) > 2:
                depth = int(col[2:])
                for c2 in ["t", "vwc"]:
                    cols.append(f"sv_{c2}{depth}")
                    if environ["qcflags"]:
                        cols.append(f"sv_{c2}{depth}_f")

    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            sql_helper(
                """
    --- Get the Daily Max/Min soil values
    WITH soils as (
      SELECT station, date(valid) as date,
      sum(
      case when (tair_c_avg_qc >= :chillbase and tair_c_avg_qc <= :chillceil)
        then 1 else 0 end) as chillhours,
      max(tair_c_max_f) as chillhours_f,
      min(rh_avg_qc) as rh_min,
      max(rh_avg_f) as rh_min_f,
      avg(rh_avg_qc) as rh,
      max(rh_avg_f) as rh_f,
      max(rh_avg_qc) as rh_max,
      max(rh_avg_f) as rh_max_f,
      min(t12_c_avg_qc) as soil12tn,
      max(t12_c_avg_f) as soil12tn_f,
      max(t12_c_avg_qc) as soil12tx,
      max(t12_c_avg_qc) as soil12tx_f,
      min(t24_c_avg_qc) as soil24tn,
      max(t24_c_avg_f) as soil24tn_f,
      max(t24_c_avg_qc) as soil24tx,
      max(t24_c_avg_f) as soil24tx_f,
      min(t50_c_avg_qc) as soil50tn,
      max(t50_c_avg_f) as soil50tn_f,
      max(t50_c_avg_qc) as soil50tx,
      max(t50_c_avg_f) as soil50tx_f
      from sm_hourly where
      valid >= :sts and valid < :ets and station = ANY(:stations)
      GROUP by station, date
    ), daily as (
      SELECT *,
      t4_c_min_qc as soil04tn,
      t4_c_min_f as soil04tn_f,
      t4_c_max_qc as soil04tx,
      t4_c_max_f as soil04tx_f,
      round(gddxx(50, 86, c2f( tair_c_max_qc ),
        c2f( tair_c_min_qc ))::numeric,1) as gdd50,
     tair_c_min_f as gdd50_f
     from sm_daily WHERE
      valid >= :sts and valid < :ets and station = ANY(:stations)
    )
    SELECT d.*, s.rh_min, s.rh_min_f, s.rh, s.rh_f, s.rh_max, s.rh_max_f,
    s.chillhours, s.chillhours_f,
    s.soil12tn, s.soil12tn_f, s.soil12tx, s.soil12tx_f, s.soil24tn,
    s.soil24tn_f, s.soil24tx, s.soil24tx_f, s.soil50tn, s.soil50tn_f,
    s.soil50tx, s.soil50tx_f
    FROM soils s JOIN daily d on (d.station = s.station and s.date = d.valid)
    ORDER by d.valid ASC
    """
            ),
            conn,
            params={
                "sts": environ["sts"].date(),
                "ets": environ["ets"].date(),
                "stations": stations,
                "chillbase": convert_value(
                    environ["chillbase"], "degF", "degC"
                ),
                "chillceil": convert_value(
                    environ["chillceil"], "degF", "degC"
                ),
            },
            index_col=None,
        )
    if df.empty:
        return df, []

    df = df.fillna(np.nan).infer_objects()

    # Direct copy / rename
    xref = {
        "rh_avg_qc": "relh",
        "rh_avg_f": "relh_f",
        "rain_in_tot_qc": "precip",
        "rain_in_tot_f": "precip_f",
        "winddir_d1_wvt_qc": "drct",
        "winddir_d1_wvt_f": "drct_f",
        "vwc12_qc": "soil12vwc",
        "vwc12_f": "soil12vwc_f",
        "vwc24_qc": "soil24vwc",
        "vwc24_f": "soil24vwc_f",
        "vwc50_qc": "soil50vwc",
        "vwc50_f": "soil50vwc_f",
        "dailyet_qc": "et",
        "dailyet_f": "et_f",
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
        df[f"{key}_f"] = df[f"{col.replace('_qc', '')}_f"]

    if "speed" in cols:
        df = df.rename(columns={"ws_mph_qc": "speed", "ws_mph_f": "speed_f"})
    if "gust" in cols:
        df = df.rename(
            columns={"ws_mph_max_qc": "gust", "ws_mph_max_f": "gust_f"}
        )
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
    else:
        for col in list(cols):
            if col.startswith("sv_r"):
                df[col] = convert_value(df[f"{col}_qc"].values, "degC", "degF")
                cols.remove(col)
            elif col.startswith("sv_vwc"):
                df[col] = df[f"{col}_qc"]
                cols.remove(col)

    # Convert solar radiation to J/m2
    if "solar" in cols:
        df["solar"] = df["slrkj_tot_qc"] * 1000.0
        df["solar_f"] = df["slrkj_tot_f"]
    if "solar_mj" in cols:
        df["solar_mj"] = df["slrkj_tot_qc"] / 1000.0
        df["solar_mj_f"] = df["slrkj_tot_f"]
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


def fetch_hourly(environ: dict, cols: list):
    """Process the request for hourly/minute data."""
    stations = environ["station"]

    if not cols:
        cols = (
            "station valid tmpf relh solar precip speed drct et soil04t "
            "soil12t soil24t soil50t soil12vwc soil24vwc soil50vwc"
        ).split()
    else:
        cols.insert(0, "valid")
        cols.insert(0, "station")
    if environ["qcflags"]:
        newcols = cols[:2]
        for col in cols[2:]:
            newcols.extend([col, f"{col}_f"])
        cols = newcols

    table = "sm_hourly"
    sqlextra = ", null as bp_mb_qc, '' as bp_mb_f "
    if environ["timeres"] == "minute":
        table = "sm_minute"
        sqlextra = ", null as etalfalfa_qc, '' as etalfalfa_f "
    if "sv" in cols:
        # SoilVue 10 data
        for depth in SV_DEPTHS:
            for c2 in ["t", "vwc"]:
                cols.append(f"sv_{c2}{depth}")
                if environ["qcflags"]:
                    cols.append(f"sv_{c2}{depth}_f")
    else:
        for col in list(cols):
            if col.startswith("sv") and len(col) > 2:
                depth = int(col[2:])
                for c2 in ["t", "vwc"]:
                    cols.append(f"sv_{c2}{depth}")
                    if environ["qcflags"]:
                        cols.append(f"sv_{c2}{depth}_f")
                # remove the proxy column
                cols.remove(col)
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            sql_helper(
                """
                SELECT *, valid at time zone 'UTC' as utc_valid {sqlextra}
                from {table} WHERE valid >= :sts and valid < :ets and
                station = ANY(:stations) ORDER by valid ASC
                """,
                table=table,
                sqlextra=sqlextra,
            ),
            conn,
            params={
                "sts": environ["sts"],
                "ets": environ["ets"],
                "stations": stations,
            },
            index_col=None,
        )
    if df.empty:
        return df, cols

    # Muck with the timestamp column
    if environ["tz"] == "UTC":
        df["valid"] = df["utc_valid"].dt.strftime("%Y-%m-%d %H:%M+00")
    else:
        df["valid"] = (
            df["utc_valid"]
            .dt.tz_localize("UTC")
            .dt.tz_convert(environ["tz"])
            .dt.strftime("%Y-%m-%d %H:%M")
        )

    df = df.fillna(np.nan).infer_objects()
    # Direct copy / rename
    xref = {
        "rh_avg_qc": "relh",
        "rh_avg_f": "relh_f",
        "rain_in_tot_qc": "precip",
        "rain_in_tot_f": "precip_f",
        "winddir_d1_wvt_qc": "drct",
        "winddir_d1_wvt_f": "drct_f",
        "vwc12_qc": "soil12vwc",
        "vwc12_f": "soil12vwc_f",
        "vwc24_qc": "soil24vwc",
        "soil24_f": "soil24vwc_f",
        "vwc50_qc": "soil50vwc",
        "soil50_f": "soil50vwc_f",
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
        df[f"{key}_f"] = df[f"{col.replace('_qc', '')}_f"]

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
    else:
        for col in cols:
            if col.startswith("sv_t"):
                df[col] = convert_value(df[f"{col}_qc"].values, "degC", "degF")
            elif col.startswith("sv_vwc"):
                # Copy
                df[col] = df[f"{col}_qc"]

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


def fetch_inversion(environ: dict, cols: list):
    """Process the request for inversion data."""
    stations = environ["station"]

    cols = "station valid tair_15 tair_5 tair_10 speed gust".split()

    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            sql_helper(
                """
                SELECT station, valid at time zone 'UTC' as utc_valid,
                tair_15_c_avg_qc,
                tair_15_c_avg_f,
                tair_5_c_avg_qc,
                tair_5_c_avg_f,
                tair_10_c_avg_qc,
                tair_10_c_avg_f,
                ws_ms_avg_qc,
                ws_ms_avg_f,
                ws_ms_max_qc,
                ws_ms_max_f
                from sm_inversion WHERE valid >= :sts and valid < :ets and
                station = ANY(:stations) ORDER by valid ASC
                """
            ),
            conn,
            params={
                "sts": environ["sts"],
                "ets": environ["ets"],
                "stations": stations,
            },
            index_col=None,
        )
    if df.empty:
        return df, cols

    # Muck with the timestamp column
    if environ["tz"] == "UTC":
        df["valid"] = df["utc_valid"].dt.strftime("%Y-%m-%d %H:%M+00")
    else:
        df["valid"] = (
            df["utc_valid"]
            .dt.tz_localize("UTC")
            .dt.tz_convert(environ["tz"])
            .dt.strftime("%Y-%m-%d %H:%M")
        )

    df = df.fillna(np.nan).infer_objects()
    # Direct copy / rename
    # Now we need to do some mass data conversion, sigh
    tc = {
        "tair_15": "tair_15_c_avg_qc",
        "tair_5": "tair_5_c_avg_qc",
        "tair_10": "tair_10_c_avg_qc",
    }
    for key, col in tc.items():
        # Do the work
        df[key] = convert_value(df[col].values, "degC", "degF")
        df[f"{key}_f"] = df[f"{col.replace('_qc', '')}_f"]

    df["speed"] = convert_value(df["ws_ms_avg_qc"].values, "mps", "mph")
    df["speed_f"] = df["ws_ms_avg_f"]
    df["gust"] = convert_value(df["ws_ms_max_qc"].values, "mps", "mph")
    df["gust_f"] = df["ws_ms_max_f"]

    return df, cols


def rewrite_cgi_params():
    """Rewrite the CGI parameters to be more sane"""

    def _decorator(func):
        def _wrapped(environ, start_response):
            """Rewrite the query string as necessary."""
            qs = environ.get("QUERY_STRING", "")
            # If sts=[A-Z] is present, we replace this with station
            if LEGACY_STS.search(qs):
                environ["QUERY_STRING"] = qs.replace("sts=", "station=")

            return func(environ, start_response)

        return _wrapped

    return _decorator


@rewrite_cgi_params()
@iemapp(
    help=__doc__, schema=Schema, default_tz="America/Chicago", parse_times=True
)
def application(environ, start_response):
    """Do things"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing start/end time parameters")
    if environ["sts"] >= environ["ets"]:
        environ["ets"] = environ["sts"] + timedelta(days=1)
    mode = environ["mode"]
    cols = environ["vars"]
    if cols is None:
        cols = []
    fmt = environ["format"]
    todisk = environ["todisk"] == "yes"
    if mode == "hourly":
        df, cols = fetch_hourly(environ, cols)
    elif mode == "inversion":
        df, cols = fetch_inversion(environ, cols)
    else:
        df, cols = fetch_daily(environ, cols)
    miss = environ["missing"]
    df = df.replace({np.nan: miss})
    # compute columns present in both cols and df.columns
    # pandas intersection is not order preserving, so we do this
    cols = [c for c in cols if c in df.columns]
    if fmt == "excel":
        bio = BytesIO()
        if cols:
            with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
                df.to_excel(
                    writer, sheet_name="Data", columns=cols, index=False
                )
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", "attachment; Filename=isusm.xlsx"),
        ]
        start_response("200 OK", headers)
        return [bio.getvalue()]

    delim = "," if fmt == "comma" else "\t"
    sio = StringIO()
    # careful of precision here
    df.to_csv(sio, index=False, columns=cols, sep=delim, float_format="%.4f")

    if todisk:
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", "attachment; filename=isusm.txt"),
        ]
    else:
        headers = [("Content-type", "text/plain")]
    start_response("200 OK", headers)
    return [sio.getvalue().encode("ascii")]
