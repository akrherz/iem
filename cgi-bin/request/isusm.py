"""Download interface for ISU-SM data."""
import datetime
from io import StringIO, BytesIO

import pandas as pd
import psycopg2.extras
from paste.request import parse_formvars
from pyiem.util import get_dbconn, c2f, mm2inch

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MISSING = {"", "M", "-99"}


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
    pgconn = get_dbconn("isuag", user="nobody")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sts, ets = get_dates(form)
    if sts is None:
        return None, None
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
            "sped",
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

    sql = """
    --- Get the Daily Max/Min soil values
    WITH soils as (
      SELECT station, date(valid) as date,
      min(rh_avg_qc) as rh_min,
      avg(rh_avg_qc) as rh,
      max(rh_avg_qc) as rh_max,
      min(t4_c_avg_qc) as soil04tn, max(t4_c_avg_qc) as soil04tx,
      min(t12_c_avg_qc) as soil12tn, max(t12_c_avg_qc) as soil12tx,
      min(t24_c_avg_qc) as soil24tn, max(t24_c_avg_qc) as soil24tx,
      min(t50_c_avg_qc) as soil50tn, max(t50_c_avg_qc) as soil50tx
      from sm_hourly where
      valid >= '%s 00:00' and valid < '%s 00:00' and station in %s
      GROUP by station, date
    ), daily as (
      SELECT station, valid, tair_c_max_qc, tair_c_min_qc, slrkj_tot_qc,
      rain_in_tot_qc, dailyet_qc, t4_c_avg_qc, t12_c_avg_qc, t24_c_avg_qc,
      t50_c_avg_qc, calc_vwc_12_avg_qc, calc_vwc_24_avg_qc, calc_vwc_50_avg_qc,
      ws_mps_s_wvt_qc, ws_mps_max_qc, lwmv_1_qc, lwmv_2_qc,
      lwmdry_1_tot_qc, lwmcon_1_tot_qc, lwmwet_1_tot_qc, lwmdry_2_tot_qc,
      lwmcon_2_tot_qc, lwmwet_2_tot_qc, bpres_avg_qc from sm_daily WHERE
      valid >= '%s 00:00' and valid < '%s 00:00' and station in %s
    )
    SELECT d.station, d.valid, s.date, s.soil04tn, s.soil04tx, s.rh,
    s.rh_min, s.rh_max,
    s.soil12tn, s.soil12tx, s.soil24tn, s.soil24tx,
    s.soil50tn, s.soil50tx, tair_c_max_qc, tair_c_min_qc, slrkj_tot_qc,
    rain_in_tot_qc, dailyet_qc, t4_c_avg_qc, t12_c_avg_qc, t24_c_avg_qc,
    t50_c_avg_qc, calc_vwc_12_avg_qc, calc_vwc_24_avg_qc, calc_vwc_50_avg_qc,
    ws_mps_s_wvt_qc, ws_mps_max_qc, round(gddxx(50, 86, c2f( tair_c_max_qc ),
    c2f( tair_c_min_qc ))::numeric,1) as gdd50, lwmv_1_qc, lwmv_2_qc,
    lwmdry_1_tot_qc, lwmcon_1_tot_qc, lwmwet_1_tot_qc, lwmdry_2_tot_qc,
    lwmcon_2_tot_qc, lwmwet_2_tot_qc, bpres_avg_qc
    FROM soils s JOIN daily d on (d.station = s.station and s.date = d.valid)
    ORDER by d.valid ASC
    """ % (
        sts.strftime("%Y-%m-%d"),
        ets.strftime("%Y-%m-%d"),
        str(tuple(stations)),
        sts.strftime("%Y-%m-%d"),
        ets.strftime("%Y-%m-%d"),
        str(tuple(stations)),
    )
    cursor.execute(sql)

    values = []
    miss = form.get("missing", "-99")
    assert miss in MISSING

    for row in cursor:
        valid = row["valid"]
        station = row["station"]
        high = (
            c2f(row["tair_c_max_qc"])
            if row["tair_c_max_qc"] is not None
            else miss
        )
        low = (
            c2f(row["tair_c_min_qc"])
            if row["tair_c_min_qc"] is not None
            else miss
        )
        precip = (
            row["rain_in_tot_qc"]
            if row["rain_in_tot_qc"] is not None and row["rain_in_tot_qc"] > 0
            else 0
        )
        et = (
            mm2inch(row["dailyet_qc"])
            if row["dailyet_qc"] is not None and row["dailyet_qc"] > 0
            else 0
        )

        soil04t = (
            c2f(row["t4_c_avg_qc"]) if row["t4_c_avg_qc"] is not None else miss
        )
        soil04tn = (
            c2f(row["soil04tn"]) if row["soil04tn"] is not None else miss
        )
        soil04tx = (
            c2f(row["soil04tx"]) if row["soil04tx"] is not None else miss
        )

        soil12t = (
            c2f(row["t12_c_avg_qc"])
            if row["t12_c_avg_qc"] is not None
            else miss
        )
        soil12tn = (
            c2f(row["soil12tn"]) if row["soil12tn"] is not None else miss
        )
        soil12tx = (
            c2f(row["soil12tx"]) if row["soil12tx"] is not None else miss
        )

        soil24t = (
            c2f(row["t24_c_avg_qc"])
            if row["t24_c_avg_qc"] is not None
            else miss
        )
        soil24tn = (
            c2f(row["soil24tn"]) if row["soil24tn"] is not None else miss
        )
        soil24tx = (
            c2f(row["soil24tx"]) if row["soil24tx"] is not None else miss
        )

        soil50t = (
            c2f(row["t50_c_avg_qc"])
            if row["t50_c_avg_qc"] is not None
            else miss
        )
        soil50tn = (
            c2f(row["soil50tn"]) if row["soil50tn"] is not None else miss
        )
        soil50tx = (
            c2f(row["soil50tx"]) if row["soil50tx"] is not None else miss
        )

        soil12vwc = (
            row["calc_vwc_12_avg_qc"]
            if row["calc_vwc_12_avg_qc"] is not None
            else miss
        )
        soil24vwc = (
            row["calc_vwc_24_avg_qc"]
            if row["calc_vwc_24_avg_qc"] is not None
            else miss
        )
        soil50vwc = (
            row["calc_vwc_50_avg_qc"]
            if row["calc_vwc_50_avg_qc"] is not None
            else miss
        )
        speed = (
            row["ws_mps_s_wvt_qc"] * 2.23
            if row["ws_mps_s_wvt_qc"] is not None
            else miss
        )
        gust = (
            row["ws_mps_max_qc"] * 2.23
            if row["ws_mps_max_qc"] is not None
            else miss
        )

        values.append(
            dict(
                station=station,
                valid=valid.strftime("%Y-%m-%d"),
                high=high,
                low=low,
                solar=row["slrkj_tot_qc"] / 1000.0,
                rh=row["rh"],
                rh_min=row["rh_min"],
                rh_max=row["rh_max"],
                gdd50=row["gdd50"],
                precip=precip,
                sped=speed,
                gust=gust,
                et=et,
                soil04t=soil04t,
                soil12t=soil12t,
                soil24t=soil24t,
                soil50t=soil50t,
                soil04tn=soil04tn,
                soil04tx=soil04tx,
                soil12tn=soil12tn,
                soil12tx=soil12tx,
                soil24tn=soil24tn,
                soil24tx=soil24tx,
                soil50tn=soil50tn,
                soil50tx=soil50tx,
                soil12vwc=soil12vwc,
                soil24vwc=soil24vwc,
                soil50vwc=soil50vwc,
                lwmv_1=row["lwmv_1_qc"],
                lwmv_2=row["lwmv_2_qc"],
                lwmdry_1_tot=row["lwmdry_1_tot_qc"],
                lwmcon_1_tot=row["lwmcon_1_tot_qc"],
                lwmwet_1_tot=row["lwmwet_1_tot_qc"],
                lwmdry_2_tot=row["lwmdry_2_tot_qc"],
                lwmcon_2_tot=row["lwmcon_2_tot_qc"],
                lwmwet_2_tot=row["lwmwet_2_tot_qc"],
                bpres_avg=row["bpres_avg_qc"],
            )
        )

    return values, cols


def fetch_hourly(form, cols):
    """Return a fetching of hourly data"""
    pgconn = get_dbconn("isuag", user="nobody")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sts, ets = get_dates(form)
    if sts is None:
        return None, None
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
    sqlextra = ", null as bp_mb_qc, etalfalfa_qc "
    if form.get("timeres") == "minute":
        table = "sm_minute"
        sqlextra = ", bp_mb_qc, null as etalfalfa_qc"
    else:
        if "bp_mb" in cols:
            cols.remove("bp_mb")
    cursor.execute(
        f"""SELECT station, valid, tair_c_avg_qc, rh_avg_qc,
    slrkj_tot_qc,
    rain_in_tot_qc, ws_mps_s_wvt_qc, winddir_d1_wvt_qc,
    t4_c_avg_qc,
    t12_c_avg_qc, t24_c_avg_qc, t50_c_avg_qc, calc_vwc_12_avg_qc,
    calc_vwc_24_avg_qc, calc_vwc_50_avg_qc, lwmv_1_qc, lwmv_2_qc,
    lwmdry_1_tot_qc, lwmcon_1_tot_qc, lwmwet_1_tot_qc, lwmdry_2_tot_qc,
    lwmcon_2_tot_qc, lwmwet_2_tot_qc, bpres_avg_qc {sqlextra}
    from {table}
    WHERE valid >= '%s 00:00' and valid < '%s 00:00' and station in %s
    ORDER by valid ASC
    """
        % (
            sts.strftime("%Y-%m-%d"),
            ets.strftime("%Y-%m-%d"),
            str(tuple(stations)),
        )
    )

    values = []
    miss = form.get("missing", "-99")
    assert miss in MISSING

    for row in cursor:
        valid = row["valid"]
        station = row["station"]
        tmpf = (
            c2f(row["tair_c_avg_qc"])
            if row["tair_c_avg_qc"] is not None
            else miss
        )
        relh = row["rh_avg_qc"] if row["rh_avg_qc"] is not None else -99
        solar = (
            (row["slrkj_tot_qc"] * 1000.0)
            if row["slrkj_tot_qc"] is not None
            else miss
        )
        precip = (
            row["rain_in_tot_qc"]
            if row["rain_in_tot_qc"] is not None
            else miss
        )
        speed = (
            row["ws_mps_s_wvt_qc"] * 2.23
            if row["ws_mps_s_wvt_qc"] is not None
            else miss
        )
        drct = (
            row["winddir_d1_wvt_qc"]
            if row["winddir_d1_wvt_qc"] is not None
            else miss
        )
        et = (
            mm2inch(row["etalfalfa_qc"])
            if row["etalfalfa_qc"] is not None
            else miss
        )
        soil04t = (
            c2f(row["t4_c_avg_qc"]) if row["t4_c_avg_qc"] is not None else miss
        )
        soil12t = (
            c2f(row["t12_c_avg_qc"])
            if row["t12_c_avg_qc"] is not None
            else miss
        )
        soil24t = (
            c2f(row["t24_c_avg_qc"])
            if row["t24_c_avg_qc"] is not None
            else miss
        )
        soil50t = (
            c2f(row["t50_c_avg_qc"])
            if row["t50_c_avg_qc"] is not None
            else miss
        )
        soil12vwc = (
            row["calc_vwc_12_avg_qc"]
            if row["calc_vwc_12_avg_qc"] is not None
            else miss
        )
        soil24vwc = (
            row["calc_vwc_24_avg_qc"]
            if row["calc_vwc_24_avg_qc"] is not None
            else miss
        )
        soil50vwc = (
            row["calc_vwc_50_avg_qc"]
            if row["calc_vwc_50_avg_qc"] is not None
            else miss
        )
        bp_mb = row["bp_mb_qc"] if row["bp_mb_qc"] is not None else -99

        values.append(
            dict(
                station=station,
                valid=valid.strftime("%Y-%m-%d %H:%M"),
                tmpf=tmpf,
                relh=relh,
                solar=solar,
                precip=precip,
                speed=speed,
                drct=drct,
                et=et,
                soil04t=soil04t,
                soil12t=soil12t,
                soil24t=soil24t,
                soil50t=soil50t,
                soil12vwc=soil12vwc,
                soil24vwc=soil24vwc,
                soil50vwc=soil50vwc,
                lwmv_1=row["lwmv_1_qc"],
                lwmv_2=row["lwmv_2_qc"],
                lwmdry_1_tot=row["lwmdry_1_tot_qc"],
                lwmcon_1_tot=row["lwmcon_1_tot_qc"],
                lwmwet_1_tot=row["lwmwet_1_tot_qc"],
                lwmdry_2_tot=row["lwmdry_2_tot_qc"],
                lwmcon_2_tot=row["lwmcon_2_tot_qc"],
                lwmwet_2_tot=row["lwmwet_2_tot_qc"],
                bpres_avg=row["bpres_avg_qc"],
                bp_mb=bp_mb,
            )
        )
    return values, cols


def application(environ, start_response):
    """Do things"""
    form = parse_formvars(environ)
    mode = form.get("mode", "hourly")
    cols = form.getall("vars")
    fmt = form.get("format", "csv").lower()
    todisk = form.get("todisk", "no")
    if mode == "hourly":
        values, cols = fetch_hourly(form, cols)
    else:
        values, cols = fetch_daily(form, cols)

    if not values:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"Sorry, no data found for this query."]

    df = pd.DataFrame(values)
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
