#!/usr/bin/env python
"""
Download interface for data from 'other' network
"""
import cgi
import datetime

import psycopg2.extras
from pyiem.util import get_dbconn, ssw


def fetcher(station, sts, ets):
    """
    Fetch the data
    """
    cols = [
        "station",
        "valid",
        "tmpf",
        "dwpf",
        "drct",
        "sknt",
        "gust",
        "relh",
        "alti",
        "pcpncnt",
        "pday",
        "pmonth",
        "srad",
        "c1tmpf",
    ]

    pgconn = get_dbconn("other", user="nobody")
    ocursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ocursor.execute(
        """
    SELECT * from alldata where station = %s and valid between %s and %s
    ORDER by valid ASC
    """,
        (station, sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")),
    )

    if ocursor.rowcount == 0:
        ssw("Sorry, no data was found for your query...\n")
        return

    ssw(
        (
            "station,valid_CST_CDT,air_tmp_F,dew_point_F,"
            "wind_dir_deg,wind_sped_kts,wind_gust_kts,relh_%,"
            "alti_in,pcpncnt_in,precip_day_in,precip_month_in,"
            "solar_rad_wms,c1tmpf\n"
        )
    )

    for row in ocursor:
        for col in cols:
            ssw("%s," % (row[col],))
        ssw("\n")


def main():
    """
    Do something!
    """
    form = cgi.FieldStorage()
    station = form.getfirst("station", "")[:10]
    year1 = int(form.getfirst("year1"))
    year2 = int(form.getfirst("year2"))
    month1 = int(form.getfirst("month1"))
    month2 = int(form.getfirst("month2"))
    day1 = int(form.getfirst("day1"))
    day2 = int(form.getfirst("day2"))

    sts = datetime.datetime(year1, month1, day1)
    ets = datetime.datetime(year2, month2, day2)
    ssw("Content-type: text/plain\n\n")
    fetcher(station, sts, ets)


if __name__ == "__main__":
    main()
