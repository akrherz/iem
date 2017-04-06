#!/usr/bin/env python
"""Generation of National Mesonet Project CSV File"""
import sys
from pyiem.network import Table as NetworkTable
import psycopg2.extras
from pyiem.datatypes import distance


def p(val, prec, minv, maxv):
    if val is None or val < minv or val > maxv:
        return 'null'
    return round(val, prec)


def do_output():
    pgconn = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
    with data as (
        select rank() OVER (ORDER by valid DESC), * from sm_hourly
        where valid > now() - '48 hours'::interval)
    SELECT *, valid at time zone 'UTC' as utc_valid from data
    where rank = 1 ORDER by station ASC""")

    sys.stdout.write(("station_id,LAT [deg N],LON [deg E],date_time,ELEV [m],"
                      "depth [m]#SOILT [C],depth [m]#SOILM [kg/kg]"
                      "\n"))

    nt = NetworkTable("ISUSM")
    for row in cursor:
        sid = row['station']
        sys.stdout.write(
            ("%s,%.4f,%.4f,%s,%.1f,"
             "%.3f;%.3f;%.3f;%.3f#%s;%s;%s;%s,"
             "%.3f;%.3f;%.3f#%s;%s;%s,"
             "\n"
             ) % (sid, nt.sts[sid]['lat'],
                  nt.sts[sid]['lon'],
                  row['utc_valid'].strftime("%Y-%m-%dT%H:%M:%SZ"),
                  nt.sts[sid]['elevation'],
                  distance(4, 'IN').value("M"), distance(12, 'IN').value("M"),
                  distance(24, 'IN').value("M"), distance(50, 'IN').value("M"),
                  p(row['tsoil_c_avg'], 3, -90, 90),
                  p(row['t12_c_avg'], 3, -90, 90),
                  p(row['t24_c_avg'], 3, -90, 90),
                  p(row['t50_c_avg'], 3, -90, 90),
                  distance(12, 'IN').value("M"),
                  distance(24, 'IN').value("M"), distance(50, 'IN').value("M"),
                  p(row['vwc_12_avg'], 1, 0, 100),
                  p(row['vwc_24_avg'], 1, 0, 100),
                  p(row['vwc_50_avg'], 1, 0, 100),
                  ))
    sys.stdout.write(".EOO\n")


def main():
    """Do Something"""
    sys.stdout.write("Content-type: text/csv;header=present\n\n")
    do_output()


if __name__ == '__main__':
    main()
