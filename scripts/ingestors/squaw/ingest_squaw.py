"""Process the Flow data provided by the USGS website"""

import re

import httpx
from pyiem.util import exponential_backoff, get_dbconn, logger

LOG = logger()


def main():
    """Squaw"""
    mydb = get_dbconn("squaw")
    cursor = mydb.cursor()

    uri = (
        "http://waterdata.usgs.gov/ia/nwis/uv?dd_cd=01&format=rdb&"
        "period=2&site_no=05470500"
    )

    req = exponential_backoff(httpx.get, uri, timeout=30)
    if req is None or req.status_code != 200:
        LOG.info("failed to fetch %s", uri)
        return
    data = req.text

    tokens = re.findall(
        "USGS\t([0-9]*)\t(....-..-.. ..:..)\t([CSDT]+)\t([0-9]*)", data
    )

    for ob in tokens:
        sql = "SELECT * from real_flow WHERE valid = '%s'" % (ob[1],)
        cursor.execute(sql)
        if cursor.rowcount > 0:
            continue
        if ob[3] != "":
            sql = """
                INSERT into real_flow(gauge_id, valid, cfs)
                VALUES (%s, '%s', %s)
            """ % (
                ob[0],
                ob[1],
                ob[3],
            )
            cursor.execute(sql)

    cursor.close()
    mydb.commit()
    mydb.close()


if __name__ == "__main__":
    main()
