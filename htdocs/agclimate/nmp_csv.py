"""Generation of National Mesonet Project CSV File"""
from io import StringIO

import numpy as np
import psycopg2.extras
from metpy.units import units
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, convert_value


def nan(val):
    """Convert to NaN, if necessary."""
    return np.nan if val is None else val


def p(val, prec, minv, maxv):
    """rounder"""
    if val is None or val < minv or val > maxv:
        return "null"
    return round(val, prec)


def p2(val, prec, minv, maxv):
    """rounder"""
    if val is None or val < minv or val > maxv:
        return "null"
    return round(convert_value(val, "degC", "degK"), prec)


def use_table(table, sio):
    """Process for the given table."""
    nt = NetworkTable("ISUSM")
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(
        """
    with data as (
        select row_number() OVER (PARTITION by station ORDER by valid DESC),
        * from """
        + table
        + """
        where valid > now() - '48 hours'::interval
        and valid < now())
    SELECT *, valid at time zone 'UTC' as utc_valid from data
    where row_number = 1 ORDER by station ASC"""
    )
    for row in cursor:
        sid = row["station"]
        sio.write(
            (
                "%s,%.4f,%.4f,%s,%.1f,"
                "%.3f;%.3f;%.3f;%.3f#%s;%s;%s;%s,"
                "%.3f;%.3f;%.3f#%s;%s;%s,"
                "%s,2#%s#%s,%s,"
                "3#%s#%s#%s"
                "\n"
            )
            % (
                sid,
                nt.sts[sid]["lat"],
                nt.sts[sid]["lon"],
                row["utc_valid"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                nt.sts[sid]["elevation"],
                convert_value(4, "inch", "meter"),
                convert_value(12, "inch", "meter"),
                convert_value(24, "inch", "meter"),
                convert_value(40, "inch", "meter"),
                p2(row["t04_c_avg_qc"], 3, -90, 90),
                p2(row["t12_c_avg_qc"], 3, -90, 90),
                p2(row["t24_c_avg_qc"], 3, -90, 90),
                p2(row["t50_c_avg_qc"], 3, -90, 90),
                convert_value(12, "inch", "meter"),
                convert_value(24, "inch", "meter"),
                convert_value(40, "inch", "meter"),
                p(row["calcvwc12_avg_qc"], 1, 0, 100),
                p(row["calcvwc24_avg_qc"], 1, 0, 100),
                p(row["calcvwc50_avg_qc"], 1, 0, 100),
                p(nan(row["slrkj_tot_qc"]) * 1000.0 / 60.0, 1, 0, 1600),
                p2(row["tair_c_avg_qc"], 1, -90, 90),
                p(row["rh_avg_qc"], 1, 0, 1600),
                p(
                    (nan(row["rain_in_tot_qc"]) * units("inch"))
                    .to(units("cm"))
                    .m,
                    2,
                    0,
                    100,
                ),
                p(
                    (nan(row["ws_mph_s_wvt_qc"]) * units("mph"))
                    .to(units("meter / second"))
                    .m,
                    2,
                    0,
                    100,
                ),
                p(
                    (nan(row["ws_mph_max_qc"]) * units("mph"))
                    .to(units("meter / second"))
                    .m,
                    2,
                    0,
                    100,
                ),
                p(row["winddir_d1_wvt_qc"], 2, 0, 360),
            )
        )


def do_output(sio):
    """Do as I say"""

    sio.write(
        (
            "station_id,LAT [degN],LON [degE],date_time,ELEV [m],"
            "depth [m]#SOILT [K],depth [m]#SOILM [kg/kg],"
            "GSRD[1]H [W/m^2],height [m]#T [K]#RH [%],"
            "PCP[1]H [mm],"
            "height [m]#FF[1]H [m/s]#FFMAX[1]H [m/s]#DD[1]H [degN]\n"
        )
    )

    use_table("sm_minute", sio)
    sio.write(".EOO\n")


def application(_environ, start_response):
    """Do Something"""
    headers = [("Content-type", "text/csv;header=present")]
    start_response("200 OK", headers)
    sio = StringIO()
    do_output(sio)
    return [sio.getvalue().encode("ascii")]
