"""Process the Flow data provided by the USGS website"""

import re

import httpx
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()


@with_sqlalchemy_conn("squaw")
def main(conn: Connection = None) -> None:
    """Squaw"""
    uri = (
        "https://waterdata.usgs.gov/ia/nwis/uv?dd_cd=01&format=rdb&"
        "period=2&site_no=05470500"
    )
    try:
        resp = httpx.get(uri, timeout=30)
        resp.raise_for_status()
    except httpx.RequestError as err:
        LOG.info("failed to fetch %s: %s", uri, err)
        return
    data = resp.text

    tokens = re.findall(
        "USGS\t([0-9]*)\t(....-..-.. ..:..)\t([CSDT]+)\t([0-9]*)", data
    )

    inserts = 0
    for ob in tokens:
        sql = "SELECT * from real_flow WHERE valid = :valid"
        rs = conn.execute(sql_helper(sql), {"valid": ob[1]})
        if rs.rowcount > 0:
            continue
        if ob[3] != "":
            sql = """
                INSERT into real_flow(gauge_id, valid, cfs)
                VALUES (:gauge_id, :valid, :cfs)
            """
            conn.execute(
                sql_helper(sql),
                {"gauge_id": ob[0], "valid": ob[1], "cfs": ob[3]},
            )
            inserts += 1

    conn.commit()
    LOG.info("Inserted %s records", inserts)


if __name__ == "__main__":
    main()
