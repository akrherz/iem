""".. title:: ISU Ag Climate GeoJSON Service

Return to `JSON Services </json/>`_

This service provides access to the ISU Ag Climate Network data in a GeoJSON
format.

Example Requests
----------------

Provide the data valid at 12 UTC on 24 July 2024:

https://mesonet.agron.iastate.edu/geojson/agclimate.py?dt=2024-07-24T12:00Z

Provide the inversion data valid at 12 UTC on 24 July 2024:

https://mesonet.agron.iastate.edu/geojson/agclimate.py\
?dt=2024-07-24T12:00Z&inversion=1

"""

import datetime
import json

from metpy.units import units
from pydantic import Field
from pyiem.meteorology import (
    comprehensive_climate_index,
    temperature_humidity_index,
)
from pyiem.network import Table as NetworkTable
from pyiem.reference import ISO8601
from pyiem.tracker import loadqc
from pyiem.util import convert_value, drct2text, mm2inch, utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    dt: str = Field(None, description="ISO8601 timestamp")
    inversion: str = Field(None, description="Set to 1 to get inversion data")


def thi(row):
    """Set to M if null."""
    if row["tair_c_avg"] is None or row["rh"] is None:
        return "M"
    return safe(
        temperature_humidity_index(
            units("degC") * row["tair_c_avg"], units("percent") * row["rh"]
        ),
        2,
    )


def cci(row, shade_effect):
    """Set to zero if null."""
    if (
        row["srad_wm2"] is None
        or row["ws_mph"] is None
        or row["rh"] is None
        or row["tair_c_avg"] is None
    ):
        return "M"
    return safe(
        comprehensive_climate_index(
            units("degC") * row["tair_c_avg"],
            units("percent") * row["rh"],
            units("miles per hour") * row["ws_mph"],
            units("W m^-2") * row["srad_wm2"],
            shade_effect=shade_effect,
        ),
        2,
    )


def safe_t(val, _units="degC"):
    """Safe value."""
    if val is None:
        return "M"
    return f"{convert_value(val, _units, 'degF'):.1f}"


def safe_p(val):
    """precipitation"""
    if val is None or val < 0:
        return "M"
    return f"{val:.2f}"


def safe(val, precision):
    """safe precision formatter"""
    if val is None or val < 0:
        return "M"
    return round(val, precision)


def safe_m(val):
    """Safe value."""
    if val is None or val < 0:
        return "M"
    return round(val * 100.0, 0)


def compute_plant_water(row):
    """Crude algo."""
    if row["vwc12_qc"] is None or row["vwc24_qc"] is None:
        return "M"
    if row["station"] == "FRUI4":  # Problematic
        return "M"
    p12 = min([max([0.1, row["vwc12_qc"]]), 0.45])
    p24 = min([max([0.1, row["vwc24_qc"]]), 0.45])
    val = (p12 * 12 + p24 * 12) - (24 * 0.1)
    return safe(val, 2)


def get_inversion_data(cursor, ts):
    """Retrieve inversion data."""
    nt = NetworkTable("ISUSM", only_online=False)
    data = {"type": "FeatureCollection", "features": []}
    cursor.execute(
        "select *, case when tair_10_c_avg > tair_15_c_avg then true else "
        "false end as is_inversion from sm_inversion where valid = %s",
        (ts,),
    )
    for row in cursor:
        sid = row["station"]
        if sid not in nt.sts:
            continue
        lon = nt.sts[sid]["lon"]
        lat = nt.sts[sid]["lat"]
        data["features"].append(
            {
                "type": "Feature",
                "id": sid,
                "properties": {
                    "name": nt.sts[sid]["name"],
                    "valid_utc": ts.strftime(ISO8601),
                    "tmpf_15": safe_t(row["tair_15_c_avg"]),
                    "tmpf_5": safe_t(row["tair_5_c_avg"]),
                    "tmpf_10": safe_t(row["tair_10_c_avg"]),
                    "is_inversion": row["is_inversion"],
                },
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        )
    return json.dumps(data)


def get_data(cursor, ts):
    """Get the data for this timestamp"""
    qcdict = loadqc()
    nt = NetworkTable("ISUSM", only_online=False)
    data = {"type": "FeatureCollection", "features": []}
    midnight = ts.replace(hour=0, minute=0)
    tophour = ts.replace(minute=0)
    h24 = ts - datetime.timedelta(hours=24)
    mon_ts0 = min([h24, ts.replace(day=1, hour=1)])
    cursor.execute(
        """
        with calendar_day as (
            select
            h.station,
            max(coalesce(h.tair_c_avg_qc, m.tair_c_avg_qc)) as max_tmpc,
            min(coalesce(h.tair_c_avg_qc, m.tair_c_avg_qc)) as min_tmpc,
            sum(coalesce(etalfalfa_qc, 0)) as dailyet,
            sum(h.rain_in_tot_qc) as pday from
            sm_minute m LEFT JOIN sm_hourly h on (m.station = h.station and
            m.valid = h.valid) WHERE m.valid > %s and m.valid <= %s
            GROUP by h.station
        ),
        twentyfour_hour as (
            select
            station,
            sum(case when valid > %s then rain_in_tot else 0 end) as p24m,
            sum(rain_in_tot) as pmonth
            from
            sm_hourly WHERE valid > %s and valid <= %s
            GROUP by station
        ),
        agg as (
            SELECT h.station,
            h.encrh_avg,
            coalesce(m.rh_avg_qc, h.rh_avg_qc) as rh,
            h.rain_in_tot,
            coalesce(etalfalfa_qc, 0) as etalfalfa_qc,
            battv_min,
            coalesce(m.slrkj_tot_qc * 60 / 1000, h.slrkj_tot_qc / 1000.)
                as slrmj_tot,
            coalesce(
                m.slrkj_tot_qc * 1000. / 60., h.slrkj_tot_qc * 1000. / 60.)
                as srad_wm2,
            coalesce(m.tair_c_avg_qc, h.tair_c_avg_qc) as tair_c_avg,
            coalesce(m.t4_c_avg_qc, h.t4_c_avg_qc) as t4_c_avg_qc,
            coalesce(
                m.t12_c_avg_qc, h.t12_c_avg_qc, m.sv_t14_qc)
                as t12_c_avg_qc,
            coalesce(m.t24_c_avg_qc, h.t24_c_avg_qc) as t24_c_avg_qc,
            coalesce(m.t50_c_avg_qc, h.t50_c_avg_qc) as t50_c_avg_qc,
            coalesce(m.vwc12_qc, h.vwc12_qc, m.sv_vwc14_qc) as vwc12_qc,
            coalesce(m.vwc24_qc, h.vwc24_qc) as vwc24_qc,
            coalesce(m.vwc50_qc, h.vwc50_qc) as vwc50_qc,
            coalesce(m.ws_mph_max, h.ws_mph_max) as ws_mph_max,
            coalesce(m.winddir_d1_wvt, h.winddir_d1_wvt) as winddir_d1_wvt,
            coalesce(m.ws_mph, coalesce(h.ws_mph, 0)) as ws_mph
            from sm_hourly h LEFT JOIN sm_minute m on (
                h.station = m.station and
                h.valid = date_trunc('hour', m.valid))
            where h.valid = %s and m.valid = %s
        )
        SELECT a.*, c.max_tmpc, c.min_tmpc, c.pday, h.p24m, h.pmonth,
        c.dailyet
        from agg a LEFT JOIN calendar_day c on (a.station = c.station)
        LEFT JOIN twentyfour_hour h on (a.station = h.station)
    """,
        (midnight, ts, h24, mon_ts0, ts, tophour, ts),
    )
    for row in cursor:
        sid = row["station"]
        if sid not in nt.sts:
            continue
        lon = nt.sts[sid]["lon"]
        lat = nt.sts[sid]["lat"]
        q = qcdict.get(sid, {})
        data["features"].append(
            {
                "type": "Feature",
                "id": sid,
                "properties": {
                    "valid_utc": ts.strftime(ISO8601),
                    "plant_water_6_30": compute_plant_water(row),
                    "encrh_avg": (
                        f"{safe(row['encrh_avg'], 1)}%"
                        if row["encrh_avg"] is not None
                        and row["encrh_avg"] > 0
                        else "M"
                    ),
                    "rh": f"{safe(row['rh'], 0)}%",
                    "hrprecip": (
                        safe_p(row["rain_in_tot"])
                        if not q.get("precip", False)
                        else "M"
                    ),
                    "et": safe_p(mm2inch(row["etalfalfa_qc"])),
                    "dailyet": (
                        safe_p(mm2inch(row["dailyet"]))
                        if row["dailyet"] is not None
                        else "M"
                    ),
                    "bat": safe(row["battv_min"], 2),
                    "cci": cci(row, False),
                    "cci_shade": cci(row, True),
                    "thi": thi(row),
                    "radmj": safe(row["slrmj_tot"], 2),
                    "srad_wm2": safe(row["srad_wm2"], 2),
                    "tmpf": (
                        safe_t(row["tair_c_avg"])
                        if not q.get("tmpf", False)
                        else "M"
                    ),
                    "high": safe_t(row["max_tmpc"], "degC"),
                    "low": safe_t(row["min_tmpc"], "degC"),
                    "pday": safe(row["pday"], 2),
                    "p24i": safe(row["p24m"], 2),
                    "pmonth": safe(row["pmonth"], 2),
                    "soil04t": (
                        safe_t(row["t4_c_avg_qc"])
                        if not q.get("soil4", False)
                        else "M"
                    ),
                    "soil12t": (
                        safe_t(row["t12_c_avg_qc"])
                        if not q.get("soil12", False)
                        else "M"
                    ),
                    "soil24t": (
                        safe_t(row["t24_c_avg_qc"])
                        if not q.get("soil24", False)
                        else "M"
                    ),
                    "soil50t": (
                        safe_t(row["t50_c_avg_qc"])
                        if not q.get("soil50", False)
                        else "M"
                    ),
                    "soil12m": (
                        safe_m(row["vwc12_qc"])
                        if not q.get("soil12", False)
                        else "M"
                    ),
                    "soil24m": (
                        safe_m(row["vwc24_qc"])
                        if not q.get("soil24", False)
                        else "M"
                    ),
                    "soil50m": (
                        safe_m(row["vwc50_qc"])
                        if not q.get("soil50", False)
                        else "M"
                    ),
                    "gust": safe(row["ws_mph_max"], 1),
                    "wind": (
                        f"{drct2text(row['winddir_d1_wvt'])}@"
                        f"{(row['ws_mph']):.0f}"
                    ),
                    "name": nt.sts[sid]["name"],
                },
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        )
    return json.dumps(data)


@iemapp(
    iemdb="isuag",
    help=__doc__,
    schema=Schema,
    content_type="application/vnd.geo+json",
    memcachekey=lambda env: f"{env['dt']}_{env['inversion']}",
    memcacheexpire=300,
)
def application(environ, start_response):
    """Go Main Go"""
    headers = [("Content-type", "application/vnd.geo+json")]
    dt = environ["dt"]
    if dt is None:
        ts = utc().replace(minute=0, second=0, microsecond=0)
    else:
        fmt = "%Y-%m-%dT%H:%M:%S.000Z" if len(dt) == 24 else "%Y-%m-%dT%H:%MZ"
        ts = datetime.datetime.strptime(dt, fmt)
        ts = ts.replace(tzinfo=datetime.timezone.utc)
    func = get_data if environ["inversion"] is None else get_inversion_data
    data = func(environ["iemdb.isuag.cursor"], ts)

    start_response("200 OK", headers)
    return data
