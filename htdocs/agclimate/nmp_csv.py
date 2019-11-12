#!/usr/bin/env python
"""Generation of National Mesonet Project CSV File"""

import psycopg2.extras
from metpy.units import units
from pyiem.network import Table as NetworkTable
from pyiem.datatypes import distance, temperature
from pyiem.util import get_dbconn, ssw


def p(val, prec, minv, maxv):
    """rounder"""
    if val is None or val < minv or val > maxv:
        return "null"
    return round(val, prec)


def p2(val, prec, minv, maxv):
    """rounder"""
    if val is None or val < minv or val > maxv:
        return "null"
    return round(temperature(val, "C").value("K"), prec)


def do_output():
    """Do as I say"""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(
        """
    with data as (
        select rank() OVER (ORDER by valid DESC), * from sm_hourly
        where valid > now() - '48 hours'::interval
        and valid < now())
    SELECT *, valid at time zone 'UTC' as utc_valid from data
    where rank = 1 ORDER by station ASC"""
    )

    ssw(
        (
            "station_id,LAT [degN],LON [degE],date_time,ELEV [m],"
            "depth [m]#SOILT [K],depth [m]#SOILM [kg/kg],"
            "GSRD[1]H [W/m^2],height [m]#T [K]#RH [%],"
            "PCP[1]H [mm],"
            "height [m]#FF[1]H [m/s]#FFMAX[1]H [m/s]#DD[1]H [degN]\n"
        )
    )

    nt = NetworkTable("ISUSM")
    for row in cursor:
        sid = row["station"]
        ssw(
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
                distance(4, "IN").value("M"),
                distance(12, "IN").value("M"),
                distance(24, "IN").value("M"),
                distance(50, "IN").value("M"),
                p2(row["tsoil_c_avg_qc"], 3, -90, 90),
                p2(row["t12_c_avg_qc"], 3, -90, 90),
                p2(row["t24_c_avg_qc"], 3, -90, 90),
                p2(row["t50_c_avg_qc"], 3, -90, 90),
                distance(12, "IN").value("M"),
                distance(24, "IN").value("M"),
                distance(50, "IN").value("M"),
                p(row["vwc_12_avg_qc"], 1, 0, 100),
                p(row["vwc_24_avg_qc"], 1, 0, 100),
                p(row["vwc_50_avg_qc"], 1, 0, 100),
                p(row["slrkw_avg_qc"], 1, 0, 1600),
                p2(row["tair_c_avg_qc"], 1, -90, 90),
                p(row["rh_qc"], 1, 0, 1600),
                p(row["rain_mm_tot_qc"], 2, 0, 100),
                p(row["ws_mps_s_wvt_qc"], 2, 0, 100),
                p(
                    (row["ws_mph_max_qc"] * units("mph"))
                    .to(units("meter / second"))
                    .m,
                    2,
                    0,
                    100,
                ),
                p(row["winddir_d1_wvt_qc"], 2, 0, 360),
            )
        )
    ssw(".EOO\n")


def main():
    """Do Something"""
    ssw("Content-type: text/csv;header=present\n\n")
    do_output()


if __name__ == "__main__":
    main()
