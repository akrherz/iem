""".. title:: IEMRE Multi-Day Data

Return to `API Services </api/>`_

Documentation for /iemre/multiday.py
------------------------------------

This application provides a JSON service for multi-day data from the IEM
Reanalysis project.

Changelog
---------

- 2025-09-26: Added ``forecast`` option to include an IEM calculated daily
  forecast from the GFS and NWS NDFD models.
- 2025-09-26: Multi-year responses are supported with the caveat that MRMS
  and PRISM data is all null in this case due to performance issues.
- 2025-09-26: The date1 parameter is now sdate and date2 parameter is edate
- 2025-01-02: Service cleanups

Example Usage
-------------

Get 1-2 January 2024 data for Ames, IA:

https://mesonet.agron.iastate.edu/iemre/multiday.py?sdate=2024-01-01&\
edate=2024-01-02&lat=42.0308&lon=-93.6319

"""

import json
import warnings
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from pydantic import Field, PrivateAttr, model_validator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.grid.nav import get_nav
from pyiem.iemre import (
    daily_offset,
    get_daily_mrms_ncname,
    get_dailyc_ncname,
    get_domain,
    get_gid,
)
from pyiem.reference import ISO8601
from pyiem.util import convert_value, ncopen, utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection

from iemweb.json.climodat_dd import compute_taxis

warnings.simplefilter("ignore", UserWarning)


# Custom JSON encoder to handle NumPy types and format floats to 2 decimals
class NumpyEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, dict):
            return super().encode(
                {k: self._convert_item(v) for k, v in obj.items()}
            )
        if isinstance(obj, list):
            return super().encode([self._convert_item(item) for item in obj])
        return super().encode(self._convert_item(obj))

    def _convert_item(self, obj):
        if isinstance(obj, (np.floating, float)):
            # Handle NaN and infinite values
            if np.isnan(obj) or np.isinf(obj):
                return None
            return round(float(obj), 2)
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: self._convert_item(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._convert_item(item) for item in obj]
        return obj


class Schema(CGIModel):
    """See how we are called."""

    _domain: str = PrivateAttr(None)
    _gid: int = PrivateAttr(None)
    _i: int = PrivateAttr(None)
    _j: int = PrivateAttr(None)

    callback: str = Field(None, description="JSONP callback function name")
    forecast: bool = Field(
        default=False,
        description=(
            "Include GFS and NWS NDFD (for CONUS requests) IEM "
            "computed daily forecasts."
        ),
    )
    sdate: date = Field(
        ..., description="Start date for the data request, YYYY-MM-DD"
    )
    edate: date = Field(
        default=date.today() - timedelta(days=1),
        description="Inclusive end date for the data request, YYYY-MM-DD",
    )
    lat: float = Field(
        ...,
        description="Latitude of the point of interest, decimal degrees",
        ge=-90,
        le=90,
    )
    lon: float = Field(
        ...,
        description="Longitude of the point of interest, decimal degrees",
        ge=-180,
        le=180,
    )

    @model_validator(mode="after")
    def ensure_domain(self):
        """Ensure the point is within a domain."""
        domain = get_domain(self.lon, self.lat)
        if domain is None:
            raise ValueError("Point is outside all IEMRE domains")
        self._domain = domain
        self._gid = get_gid(self.lon, self.lat, domain)
        self._i, self._j = get_nav("iemre", domain).find_ij(self.lon, self.lat)


def get_iemre(
    conn: Connection, ts1: date, ts2: date, model: Schema
) -> pd.DataFrame:
    """Get IEMRE data from the database."""
    df = pd.read_sql(
        sql_helper("""
    select *,
    to_char(valid, 'YYYY-MM-DD') as date,
    null as climate_daily_high_f,
    null as climate_daily_low_f,
    null as climate_daily_precip_in,
    null as mrms_precip_in,
    null as prism_precip_in,
    null as avg_dewpoint_f
    from iemre_daily
    where gid = :gid and valid >= :sdate and valid <= :edate ORDER by valid asc
        """),
        conn,
        params={"gid": model._gid, "sdate": ts1, "edate": ts2},
        index_col="valid",
    )

    # Convert numeric columns with NULLs from object dtype to float64 with
    # np.nan
    numeric_columns = [
        "high_tmpk",
        "low_tmpk",
        "high_tmpk_12z",
        "low_tmpk_12z",
        "avg_dwpk",
        "high_soil4t",
        "low_soil4t",
        "p01d",
        "p01d_12z",
        "rsds",
        "climate_daily_high_f",
        "climate_daily_low_f",
        "climate_daily_precip_in",
        "mrms_precip_in",
        "prism_precip_in",
        "avg_dewpoint_f",
    ]

    for col in numeric_columns:
        if col in df.columns and df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def add_forecast(res: dict, model: Schema):
    """Include forecast info into res."""
    for fxmodel in ["gfs", "ndfd"]:
        if fxmodel == "ndfd" and model._domain != "":
            continue
        res[f"{fxmodel}_forecast"] = []
        extra = "" if model._domain == "" else f"_{model._domain}"
        ncfn = f"/mesonet/data/iemre{extra}/{fxmodel}_current.nc"
        if not Path(ncfn).exists():
            continue
        with ncopen(ncfn) as nc:
            taxis = compute_taxis(nc.variables["time"])
            highs = convert_value(
                nc.variables["high_tmpk"][:, model._j, model._i],
                "degK",
                "degF",
            )
            lows = convert_value(
                nc.variables["low_tmpk"][:, model._j, model._i],
                "degK",
                "degF",
            )
            for t, h, lo in zip(taxis, highs, lows, strict=True):
                res[f"{fxmodel}_forecast"].append(
                    {"date": f"{t:%Y-%m-%d}", "high_f": h, "low_f": lo}
                )


def get_mckey(environ: dict):
    """Figure out the memcache key."""
    model: Schema = environ["_cgimodel_schema"]
    return (
        f"iemre/multiday/{model._domain}/{environ['sdate']:%Y%m%d}"
        f"/{environ['edate']:%Y%m%d}/{model._i}/{model._j}"
        f"/{environ['forecast']}"
    )


@iemapp(
    help=__doc__, schema=Schema, memcachekey=get_mckey, memcacheexpire=3600
)
def application(environ, start_response):
    """Go Main Go"""
    begin_ts = utc()
    model: Schema = environ["_cgimodel_schema"]
    ts1: date = environ["sdate"]
    ts2: date = environ["edate"]
    if ts1 > ts2:
        (ts1, ts2) = (ts2, ts1)

    is_single_year = ts1.year == ts2.year

    res = {
        "generated_at": utc().strftime(ISO8601),
        "iemre_domain": model._domain,
        "iemre_i": model._i,
        "iemre_j": model._j,
        "data": [],
        "timing_seconds": 0,
    }

    extra = "" if model._domain == "" else f"_{model._domain}"
    with get_sqlalchemy_conn(f"iemre{extra}") as conn:
        iemredf = get_iemre(conn, ts1, ts2, model)

    if iemredf.empty:
        res["timing_seconds"] = (utc() - begin_ts).total_seconds()
        start_response("200 OK", [("Content-type", "application/json")])
        return [json.dumps(res, cls=NumpyEncoder).encode("ascii")]

    # Ensure our arrays align, I hope
    tslice = None
    if is_single_year:
        offset1 = daily_offset(iemredf.index[0])
        offset2 = daily_offset(iemredf.index[-1]) + 1
        tslice = slice(offset1, offset2)

    iemredf["daily_high_f"] = convert_value(
        iemredf["high_tmpk"].to_numpy(), "degK", "degF"
    )
    iemredf["12z_high_f"] = convert_value(
        iemredf["high_tmpk_12z"].to_numpy(), "degK", "degF"
    )
    iemredf["daily_low_f"] = convert_value(
        iemredf["low_tmpk"].to_numpy(), "degK", "degF"
    )
    iemredf["12z_low_f"] = convert_value(
        iemredf["low_tmpk_12z"].to_numpy(), "degK", "degF"
    )
    iemredf["avg_dewpoint_f"] = convert_value(
        iemredf["avg_dwpk"].to_numpy(), "degK", "degF"
    )
    iemredf["soil4t_high_f"] = convert_value(
        iemredf["high_soil4t"].to_numpy(), "degK", "degF"
    )
    iemredf["soil4t_low_f"] = convert_value(
        iemredf["low_soil4t"].to_numpy(), "degK", "degF"
    )
    iemredf["daily_precip_in"] = convert_value(
        iemredf["p01d"].to_numpy(), "mm", "in"
    )
    iemredf["12z_precip_in"] = convert_value(
        iemredf["p01d_12z"].to_numpy(),
        "mm",
        "in",
    )
    iemredf["solar_mj"] = iemredf["rsds"].to_numpy() / 1e6 * 86400.0

    # Get our climatology vars
    ncfn = Path(get_dailyc_ncname(domain=model._domain))
    if ncfn.exists():
        with ncopen(ncfn) as cnc:
            chigh = convert_value(
                cnc.variables["high_tmpk"][:, model._j, model._i],
                "degK",
                "degF",
            )
            clow = convert_value(
                cnc.variables["low_tmpk"][:, model._j, model._i],
                "degK",
                "degF",
            )
            cprecip = convert_value(
                cnc.variables["p01d"][:, model._j, model._i], "mm", "in"
            )
            for dt in iemredf.index:
                doy = dt.timetuple().tm_yday - 1
                iemredf.at[dt, "climate_daily_high_f"] = chigh[doy]
                iemredf.at[dt, "climate_daily_low_f"] = clow[doy]
                iemredf.at[dt, "climate_daily_precip_in"] = cprecip[doy]

    if is_single_year and ts1.year > 1980 and model._domain == "":
        i2, j2 = get_nav("prism", "").find_ij(environ["lon"], environ["lat"])
        if i2 is not None and j2 is not None:
            res["prism_grid_i"] = i2
            res["prism_grid_j"] = j2
            ncfn = Path(f"/mesonet/data/prism/{ts1.year}_daily.nc")
            if ncfn.exists():
                with ncopen(ncfn) as nc:
                    iemredf["prism_precip_in"] = convert_value(
                        nc.variables["ppt"][tslice, j2, i2], "mm", "in"
                    )

    if is_single_year and ts1.year > 2000 and model._domain == "":
        i2, j2 = get_nav("mrms_iemre", "").find_ij(
            environ["lon"], environ["lat"]
        )
        res["mrms_iemre_grid_i"] = i2
        res["mrms_iemre_grid_j"] = j2
        ncfn = Path(get_daily_mrms_ncname(ts1.year))
        if ncfn.exists():
            with ncopen(ncfn) as nc:
                iemredf["mrms_precip_in"] = convert_value(
                    nc.variables["p01d"][tslice, j2, i2], "mm", "in"
                )

    cols = (
        "date mrms_precip_in prism_precip_in daily_high_f 12z_high_f "
        "climate_daily_high_f daily_low_f 12z_low_f avg_dewpoint_f "
        "soil4t_high_f soil4t_low_f climate_daily_low_f daily_precip_in "
        "12z_precip_in climate_daily_precip_in solar_mj"
    ).split()

    res["data"] = iemredf[cols].to_dict(orient="records")
    if environ["forecast"]:
        add_forecast(res, model)

    res["timing_seconds"] = (utc() - begin_ts).total_seconds()
    start_response("200 OK", [("Content-type", "application/json")])
    return [json.dumps(res, cls=NumpyEncoder).encode("ascii")]
