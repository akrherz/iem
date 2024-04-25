"""Ingest the purple air sensor.

Called from RUN_1MIN.sh
"""

import httpx
from pyiem.database import get_dbconnc
from pyiem.observation import Observation
from pyiem.util import utc


def main():
    """Go Main Go."""
    # http://10.26.117.91/json?live=false
    with httpx.Client() as client:
        req = client.get("http://10.26.117.91/json?live=false", timeout=15)
        data = req.json()

    ob = Observation("OT0017", "OT", utc())
    ob.data["tmpf"] = data["current_temp_f"]
    ob.data["relh"] = data["current_humidity"]
    ob.data["dwpf"] = data["current_dewpoint_f"]
    ob.data["pres"] = data["pressure"]
    conn, cursor = get_dbconnc("iem")
    ob.save(cursor)
    cursor.close()
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
