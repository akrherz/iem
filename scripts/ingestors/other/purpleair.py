"""Ingest the purple air sensor.

Called from RUN_1MIN.sh
"""

import httpx
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.observation import Observation
from pyiem.util import utc
from sqlalchemy import text

XREF = {
    "pm2_5_aqi_b": "pm2.5_aqi_b",
    "pm2_5_aqi": "pm2.5_aqi",
}


def save_other(data):
    """Write to the database."""
    for key, val in XREF.items():
        data[key] = data[val]
    data["station"] = "OT0017"
    data["valid"] = utc()
    with get_sqlalchemy_conn("other") as conn:
        # retrieve all the columns within the purpleair table
        res = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'purpleair' and table_schema = 'public'"
            )
        )
        columns = [row[0] for row in res]
        # do a bulk insert
        vals = [f":{x}" for x in columns]
        conn.execute(
            text(
                f"insert into purpleair ({','.join(columns)}) "
                f"values ({','.join(vals)}) "
            ),
            data,
        )
        conn.commit()


def main():
    """Go Main Go."""
    # http://10.26.117.91/json?live=false
    with httpx.Client() as client:
        req = client.get("http://10.26.117.91/json?live=false", timeout=15)
        data = req.json()

    save_other(data)

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
