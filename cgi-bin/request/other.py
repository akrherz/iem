#!/usr/bin/env python
"""
Download interface for data from 'other' network
"""
import sys
import cgi
import datetime

from pyiem.util import get_dbconn
import psycopg2.extras


def fetcher(station, sts, ets):
    """
    Fetch the data
    """
    cols = ['station', 'valid', 'tmpf', 'dwpf', 'drct', 'sknt', 'gust',
            'relh', 'alti', 'pcpncnt', 'pday', 'pmonth', 'srad', 'c1tmpf']

    pgconn = get_dbconn('other', user='nobody')
    ocursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ocursor.execute("""
    SELECT * from alldata where station = %s and valid between %s and %s
    ORDER by valid ASC
    """, (station, sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")))

    if ocursor.rowcount == 0:
        sys.stdout.write("Sorry, no data was found for your query...\n")
        return

    sys.stdout.write(("station,valid_CST_CDT,air_tmp_F,dew_point_F,"
                      "wind_dir_deg,wind_sped_kts,wind_gust_kts,relh_%,"
                      "alti_in,pcpncnt_in,precip_day_in,precip_month_in,"
                      "solar_rad_wms,c1tmpf\n"))

    for row in ocursor:
        for col in cols:
            sys.stdout.write("%s," % (row[col],))
        sys.stdout.write("\n")


def main():
    """
    Do something!
    """
    form = cgi.FormContent()
    station = form['station'][0][:10]
    year1 = int(form["year1"][0])
    year2 = int(form["year2"][0])
    month1 = int(form["month1"][0])
    month2 = int(form["month2"][0])
    day1 = int(form["day1"][0])
    day2 = int(form["day2"][0])

    sts = datetime.datetime(year1, month1, day1)
    ets = datetime.datetime(year2, month2, day2)
    sys.stdout.write("Content-type: text/plain\n\n")
    fetcher(station, sts, ets)


if __name__ == '__main__':
    main()
