"""Ingest Iowa DOT RWIS data provided by DTN."""
import datetime

from pyiem.network import Table as NetworkTable
from pyiem.util import get_properties, get_dbconn, utc, logger
import pandas as pd
import requests

LOG = logger()
DBCONN = get_dbconn("iem")
NT = NetworkTable("IA_RWIS")


def load_metadata():
    """Load up what we know about these traffic sites."""
    meta = {}
    cur = DBCONN.cursor()
    cur.execute(
        """
        SELECT location_id, lane_id, sensor_id from rwis_traffic_meta
    """
    )
    rows = cur.fetchall()
    cur.close()
    for row in rows:
        key = f"{row[0]}_{row[1]}"
        meta[key] = row[2]
    return meta


def create_sensor(cursor, key, row, meta):
    """create an entry."""
    cursor.execute(
        """
            INSERT into rwis_traffic_sensors(location_id,
            lane_id, name) VALUES (%s, %s, %s) RETURNING id
     """,
        (
            row["stationId"].replace("IA", ""),
            row["sensorId"],
            row["sensorName"],
        ),
    )
    sensor_id = cursor.fetchone()[0]
    LOG.info(
        "Adding RWIS Traffic Sensor: %s Lane: %s Name: %s DB_SENSOR_ID: %s",
        row["stationId"],
        row["sensorId"],
        row["sensorName"],
        sensor_id,
    )
    meta[key] = sensor_id
    cursor.execute(
        """
        INSERT into rwis_traffic_data(sensor_id) VALUES (%s)
        """,
        (sensor_id,),
    )


def process(cursor, df, meta):
    """Process our data."""
    rows = []
    for _, row in df.iterrows():
        data = dict(row)
        key = f"{int(row['stationId'].replace('IA', ''))}_{row['sensorId']}"
        if key not in meta:
            create_sensor(cursor, key, row, meta)
        data["sensor_id"] = meta[key]
        rows.append(data)
    # 'volume',
    # 'occupancy',
    # 'normalLength', 'longLength', 'unclassifiedLength', 'qcFailures'
    cursor.executemany(
        """UPDATE rwis_traffic_data SET
      valid = %(utcTime)s, avg_speed = %(avgSpeed)s,
      normal_vol = %(normalLength)s,
      long_vol = %(longLength)s,  occupancy = %(occupancy)s
      WHERE sensor_id = %(sensor_id)s""",
        rows,
    )


def main():
    """Go Main Go."""
    ets = utc()
    sts = ets - datetime.timedelta(days=1)
    edate = ets.strftime("%Y-%m-%dT%H:%M:%SZ")
    sdate = sts.strftime("%Y-%m-%dT%H:%M:%SZ")
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

        req = requests.get(URI, headers=headers)
        res = req.json()
        if not res:
            continue
        df = pd.DataFrame(res)
        cursor = DBCONN.cursor()
        process(cursor, df, meta)
        cursor.close()
        DBCONN.commit()


if __name__ == "__main__":
    main()
