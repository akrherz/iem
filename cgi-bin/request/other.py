"""
Download interface for data from 'other' network
"""
from io import StringIO

from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_dbconnc
from pyiem.webutil import iemapp


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
    ]

    pgconn, cursor = get_dbconnc("other")
    cursor.execute(
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
            "solar_rad_wms\n"
        )
    )

    for row in cursor:
        sio.write(",".join(f"{row[col]}" for col in cols))
        sio.write("\n")
    pgconn.close()
    return sio.getvalue().encode("ascii")


@iemapp()
def application(environ, start_response):
    """
    Do something!
    """
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start time parameters missing")
    station = environ.get("station", "")[:10]
    start_response("200 OK", [("Content-type", "text/plain")])
    return [fetcher(station, environ["sts"], environ["ets"])]
