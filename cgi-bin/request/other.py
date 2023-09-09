"""
Download interface for data from 'other' network
"""
import datetime
from io import StringIO

import psycopg2.extras
from paste.request import parse_formvars
from pyiem.util import get_dbconn


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

    pgconn = get_dbconn("other")
    ocursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    ocursor.execute(
        """
    SELECT * from alldata where station = %s and valid between %s and %s
    ORDER by valid ASC
    """,
        (station, sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")),
    )

    sio = StringIO()
    sio.write(
        (
            "station,valid_CST_CDT,air_tmp_F,dew_point_F,"
            "wind_dir_deg,wind_sped_kts,wind_gust_kts,relh_%,"
            "alti_in,pcpncnt_in,precip_day_in,precip_month_in,"
            "solar_rad_wms,c1tmpf\n"
        )
    )

    for row in ocursor:
        sio.write(",".join(f"{row[col]}" for col in cols))
        sio.write("\n")
    return sio.getvalue().encode("ascii")


def application(environ, start_response):
    """
    Do something!
    """
    form = parse_formvars(environ)
    station = form.get("station", "")[:10]
    year1 = int(form.get("year1"))
    year2 = int(form.get("year2"))
    month1 = int(form.get("month1"))
    month2 = int(form.get("month2"))
    day1 = int(form.get("day1"))
    day2 = int(form.get("day2"))

    sts = datetime.datetime(year1, month1, day1)
    ets = datetime.datetime(year2, month2, day2)
    start_response("200 OK", [("Content-type", "text/plain")])
    return [fetcher(station, sts, ets)]
