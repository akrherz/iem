""" Produce geojson of ISUSM data """
import datetime
import json

import pytz
import psycopg2.extras
from paste.request import parse_formvars
from pyiem.network import Table as NetworkTable
from pyiem.tracker import loadqc
from pyiem.util import drct2text, get_dbconn, utc, convert_value


def safe_t(val, units="degC"):
    """Safe value."""
    if val is None:
        return "M"
    return "%.1f" % (convert_value(val, units, "degF"),)


def safe_p(val):
    """precipitation"""
    if val is None or val < 0:
        return "M"
    return "%.2f" % (val,)


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


def get_data(pgconn, ts):
    """Get the data for this timestamp"""
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    qcdict = loadqc()
    nt = NetworkTable("ISUSM", only_online=False)
    data = {"type": "FeatureCollection", "features": []}
    midnight = ts.replace(hour=0)
    h24 = ts - datetime.timedelta(hours=24)
    cursor.execute(
        """
        with calendar_day as (
            select
            h.station,
            max(coalesce(h.tair_c_avg_qc, m.tair_c_avg_qc)) as max_tmpc,
            min(coalesce(h.tair_c_avg_qc, m.tair_c_avg_qc)) as min_tmpc,
            sum(h.rain_in_tot_qc) as pday from
            sm_minute m LEFT JOIN sm_hourly h on (m.station = h.station and
            m.valid = h.valid) WHERE m.valid > %s and m.valid <= %s
            GROUP by h.station
        ),
        twentyfour_hour as (
            select
            station,
            sum(rain_in_tot) as p24m from
            sm_hourly WHERE valid > %s and valid <= %s
            GROUP by station
        ),
        agg as (
            SELECT h.station,
            h.encrh_avg,
            coalesce(m.rh_avg_qc, h.rh_avg_qc) as rh,
            h.rain_in_tot,
            etalfalfa,
            battv_min,
            coalesce(m.slrkj_tot_qc * 60 / 1000, h.slrkj_tot_qc / 1000.)
                as slrmj_tot,
            coalesce(
                m.slrkj_tot_qc * 1000. / 60., h.slrkj_tot_qc * 1000. / 60.)
                as srad_wm2,
            coalesce(m.tair_c_avg_qc, h.tair_c_avg_qc) as tair_c_avg,
            coalesce(m.t04_c_avg_qc, h.t04_c_avg_qc) as t04_c_avg_qc,
            coalesce(m.t12_c_avg_qc, h.t12_c_avg_qc) as t12_c_avg_qc,
            coalesce(m.t24_c_avg_qc, h.t24_c_avg_qc) as t24_c_avg_qc,
            coalesce(m.t50_c_avg_qc, h.t50_c_avg_qc) as t50_c_avg_qc,
            coalesce(m.calcvwc12_avg_qc, h.calc_vwc_12_avg_qc)
                as calc_vwc_12_avg_qc,
            coalesce(m.calcvwc24_avg_qc, h.calc_vwc_24_avg_qc)
                as calc_vwc_24_avg_qc,
            coalesce(m.calcvwc50_avg_qc, h.calc_vwc_50_avg_qc)
                as calc_vwc_50_avg_qc,
            coalesce(m.ws_mph_max, h.ws_mph_max) as ws_mph_max,
            coalesce(m.winddir_d1_wvt, h.winddir_d1_wvt) as winddir_d1_wvt,
            coalesce(m.ws_mph_s_wvt * 0.447,
                    coalesce(h.ws_mps_s_wvt, 0))as ws_mps_s_wvt
            from sm_hourly h LEFT JOIN sm_minute m on (
                h.station = m.station and h.valid = m.valid)
            where h.valid = %s
        )
        SELECT a.*, c.max_tmpc, c.min_tmpc, c.pday, h.p24m from
        agg a LEFT JOIN calendar_day c on (a.station = c.station)
        LEFT JOIN twentyfour_hour h on (a.station = h.station)
    """,
        (midnight, ts, h24, ts, ts),
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
                    "valid_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "encrh_avg": (
                        "%s%%" % safe(row["encrh_avg"], 1)
                        if row["encrh_avg"] is not None
                        and row["encrh_avg"] > 0
                        else "M"
                    ),
                    "rh": "%s%%" % (safe(row["rh"], 0),),
                    "hrprecip": (
                        safe_p(row["rain_in_tot"])
                        if not q.get("precip", False)
                        else "M"
                    ),
                    "et": safe_p(row["etalfalfa"]),
                    "bat": safe(row["battv_min"], 2),
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
                    "soil04t": (
                        safe_t(row["t04_c_avg_qc"])
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
                        safe_m(row["calc_vwc_12_avg_qc"])
                        if not q.get("soil12", False)
                        else "M"
                    ),
                    "soil24m": (
                        safe_m(row["calc_vwc_24_avg_qc"])
                        if not q.get("soil24", False)
                        else "M"
                    ),
                    "soil50m": (
                        safe_m(row["calc_vwc_50_avg_qc"])
                        if not q.get("soil50", False)
                        else "M"
                    ),
                    "gust": safe(row["ws_mph_max"], 1),
                    "wind": ("%s@%.0f")
                    % (
                        drct2text(row["winddir_d1_wvt"]),
                        row["ws_mps_s_wvt"] * 2.23,
                    ),
                    "name": nt.sts[sid]["name"],
                },
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        )
    return json.dumps(data)


def application(environ, start_response):
    """Go Main Go"""
    headers = [("Content-type", "application/vnd.geo+json")]
    field = parse_formvars(environ)
    dt = field.get("dt")
    if dt is None:
        ts = utc().replace(minute=0, second=0, microsecond=0)
    else:
        ts = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.000Z")
        ts = ts.replace(tzinfo=datetime.timezone.utc)
    with get_dbconn("isuag") as pgconn:
        data = get_data(
            pgconn,
            ts.astimezone(pytz.timezone("America/Chicago")),
        )

    start_response("200 OK", headers)
    return [data.encode("ascii")]
