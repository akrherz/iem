"""SPC MCD service."""
import json

from pyiem.util import get_dbconn, html_escape
from pyiem.webutil import iemapp

ISO9660 = "%Y-%m-%dT%H:%MZ"
BASEURL = "https://www.spc.noaa.gov/products/md"


def dowork(count, sort):
    """Actually do stuff"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    res = dict(mcds=[])

    cursor.execute(
        f"""
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e, num, product_id, year,
        ST_Area(geom::geography) / 1000000. as area_sqkm,
        concerning from mcd WHERE not ST_isEmpty(geom)
        ORDER by area_sqkm {sort} LIMIT %s
    """,
        (count,),
    )
    for row in cursor:
        url = f"{BASEURL}/{row[4]}/md{row[2]:04.0f}.html"
        res["mcds"].append(
            dict(
                spcurl=url,
                year=row[4],
                utc_issue=row[0].strftime(ISO9660),
                utc_expire=row[1].strftime(ISO9660),
                product_num=row[2],
                product_id=row[3],
                area_sqkm=row[5],
                concerning=row[6],
            )
        )

    return json.dumps(res)


@iemapp()
def application(environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)

    count = int(environ.get("count", 10))
    sort = environ.get("sort", "DESC").upper()
    if sort not in ["ASC", "DESC"]:
        return [b"provided `sort` not in {ASC,DESC}"]

    cb = environ.get("callback")

    res = dowork(count, sort)
    if cb is None:
        data = res
    else:
        data = f"{html_escape(cb)}({res})"

    return [data.encode("ascii")]
