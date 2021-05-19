""" Produce geojson of ISUSM data """
import datetime
import json

import pytz
import psycopg2.extras
from paste.request import parse_formvars
from pyiem.network import Table as NetworkTable
from pyiem.tracker import loadqc
from pyiem.util import drct2text, get_dbconn, utc, convert_value

ISUAG = get_dbconn("isuag")
IEM = get_dbconn("iem")


def safe_t(val, units="degC"):
    """Safe value."""
    if val is None:
        return "M"
    return "%.1f" % (convert_value(val, units, "degF"),)


def safe_p(val):
    """precipitation"""
    if val is None or val < 0:
        return "M"
    return "%.2f" % (val / 25.4,)


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


def get_data(ts):
    """Get the data for this timestamp"""
    iemcursor = IEM.cursor()
    cursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)
    qcdict = loadqc()
    nt = NetworkTable("ISUSM", only_online=False)
    data = {"type": "FeatureCollection", "features": []}
    # Fetch the daily values
    iemcursor.execute(
        "SELECT id, pday, max_tmpf, min_tmpf from summary s JOIN stations t "
        "on (t.iemid = s.iemid) WHERE t.network = 'ISUSM' and day = %s",
        (ts.date(),),
    )
    daily = {}
    for row in iemcursor:
        daily[row[0]] = {
            "pday": row[1],
            "max_tmpf": row[2],
            "min_tmpf": row[3],
        }
    cursor.execute(
        """
    SELECT h.station,
        h.encrh_avg,
        coalesce(m.rh_avg_qc, h.rh_qc) as rh,
        h.rain_mm_tot,
        etalfalfa,
        battv_min,
        coalesce(m.slrkj_tot_qc * 3600 / 1000000, h.slrmj_tot_qc) as slrmj_tot,
        coalesce(m.tair_c_avg, h.tair_c_avg) as tair_c_avg,
        coalesce(m.tsoil_c_avg_qc, h.tsoil_c_avg_qc) as tsoil_c_avg_qc,
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
    from sm_hourly h LEFT JOIN sm_minute m on (h.station = m.station and
    h.valid = m.valid)
    where h.valid = %s
    """,
        (ts,),
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
                        safe_p(row["rain_mm_tot"])
                        if not q.get("precip", False)
                        else "M"
                    ),
                    "et": safe_p(row["etalfalfa"]),
                    "bat": safe(row["battv_min"], 2),
                    "radmj": safe(row["slrmj_tot"], 2),
                    "tmpf": safe_t(row["tair_c_avg"]),
                    "high": safe_t(
                        daily.get(sid, {}).get("max_tmpf", None), "degF"
                    ),
                    "low": safe_t(
                        daily.get(sid, {}).get("min_tmpf", None), "degF"
                    ),
                    "pday": (
                        safe(daily.get(sid, {}).get("pday", None), 2)
                        if not q.get("precip", False)
                        else "M"
                    ),
                    "soil04t": (
                        safe_t(row["tsoil_c_avg_qc"])
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
        ts = ts.replace(tzinfo=pytz.UTC)
    data = get_data(ts)

    start_response("200 OK", headers)
    return [data.encode("ascii")]
