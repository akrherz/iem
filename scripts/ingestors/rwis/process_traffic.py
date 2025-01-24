"""Ingest Iowa DOT RWIS data provided by DTN.

called from RUN_10_AFTER.sh
"""

from datetime import timedelta

import httpx
import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.network import Table as NetworkTable
from pyiem.reference import ISO8601
from pyiem.util import get_properties, logger, utc

LOG = logger()
NT = NetworkTable("IA_RWIS")


def load_metadata():
    """Load up what we know about these traffic sites."""
    meta = {}
    conn, icursor = get_dbconnc("iem")
    icursor.execute(
        "SELECT location_id, lane_id, sensor_id from rwis_traffic_meta"
    )
    for row in icursor:
        key = f"{row['location_id']}_{row['lane_id']}"
        meta[key] = row["sensor_id"]
    icursor.close()
    conn.close()
    return meta


def create_sensor(cursor, key, row, meta):
    """create an entry."""
    cursor.execute(
        "INSERT into rwis_traffic_sensors(location_id, lane_id, name) "
        "VALUES (%s, %s, %s) RETURNING id",
        (
            row["stationId"].replace("IA", ""),
            row["sensorId"],
            row["sensorName"],
        ),
    )
    sensor_id = cursor.fetchone()["id"]
    LOG.info(
        "Adding RWIS Traffic Sensor: %s Lane: %s Name: %s DB_SENSOR_ID: %s",
        row["stationId"],
        row["sensorId"],
        row["sensorName"],
        sensor_id,
    )
    meta[key] = sensor_id
    cursor.execute(
        "INSERT into rwis_traffic_data(sensor_id) VALUES (%s)", (sensor_id,)
    )


def process(cursor, df, meta):
    """Process our data."""
    rows = []
    for _, row in df.iterrows():
        data = dict(row)
        if "stationId" not in data:
            LOG.info("hit data quirk with row %s", row)
            continue
        key = f"{int(row['stationId'].replace('IA', ''))}_{row['sensorId']}"
        if key not in meta:
            create_sensor(cursor, key, row, meta)
        data["sensor_id"] = meta[key]
        rows.append(data)
    # 'volume',
    # 'occupancy',
    # 'normalLength', 'longLength', 'unclassifiedLength', 'qcFailures'
    cursor.executemany(
        """
        UPDATE rwis_traffic_data SET valid = %(utcTime)s,
        avg_speed = %(avgSpeed)s, normal_vol = %(normalLength)s,
        long_vol = %(longLength)s,  occupancy = %(occupancy)s, updated = now()
        WHERE sensor_id = %(sensor_id)s and valid < %(utcTime)s
        """,
        rows,
    )


def main():
    """Go Main Go."""
    # prevent a clock drift issue
    ets = utc() - timedelta(minutes=1)
    sts = ets - timedelta(hours=4)
    edate = ets.strftime(ISO8601)
    sdate = sts.strftime(ISO8601)
    meta = load_metadata()
    props = get_properties()
    apikey = props["dtn.apikey"]
    headers = {"accept": "application/json", "apikey": apikey}
    for nwsli in NT.sts:
        idot_id = NT.sts[nwsli]["remote_id"]
        if idot_id is None:
            continue
        URI = (
            f"https://api.dtn.com/weather/stations/IA{idot_id:03}/"
            f"traffic-observations?startDate={sdate}"
            f"&endDate={edate}&units=us&precision=0"
        )

        resp = httpx.get(URI, timeout=60, headers=headers)
        if resp.status_code != 200:
            # HACK
            if idot_id < 73:
                LOG.info("Fetch %s got status_code %s", URI, resp.status_code)
            continue
        res = resp.json()
        if not res:
            continue
        try:
            df = pd.DataFrame(res)
        except Exception as exp:
            LOG.info(
                "DataFrame construction failed with %s\n res: %s", exp, res
            )
            continue
        conn, cursor = get_dbconnc("iem")
        process(cursor, df, meta)
        cursor.close()
        conn.commit()
        conn.close()


if __name__ == "__main__":
    main()
