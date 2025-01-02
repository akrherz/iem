"""Process Soil Data"""

# stdlib
import datetime
import json
import sys
from zoneinfo import ZoneInfo

import httpx

# third party
import pandas as pd
from pyiem.util import (
    exponential_backoff,
    get_dbconn,
    get_sqlalchemy_conn,
    logger,
)

LOG = logger()
URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/arcgis/rest/services/"
    "RWIS_SubSurface_All_View/FeatureServer/0/query?where=TEMPERATURE<999&"
    "f=json&outFields=NWS_ID,TEMPERATURE,DATA_LAST_UPDATED,SENSOR_ID"
)


def clean2(val):
    """Clean again."""
    return None if pd.isnull(val) else val


def clean(val):
    """Clean our value."""
    if val is None:
        return None
    try:
        val = float(val)
        if val > 200 or val < -50:
            val = None
    except ValueError:
        val = None
    return val


def process_features(features):
    """Process this feature."""
    rows = []
    for feat in features:
        props = feat["attributes"]
        valid = (
            datetime.datetime(1970, 1, 1)
            + datetime.timedelta(seconds=props["DATA_LAST_UPDATED"] / 1000.0)
        ).replace(tzinfo=ZoneInfo("UTC"))
        rows.append(
            {
                "nwsli": props["NWS_ID"],
                "tmpf": clean(props.get("TEMPERATURE")),
                "valid": valid,
                "sensor_id": props["SENSOR_ID"],
            }
        )
    if not rows:
        LOG.info("No data, aborting")
        sys.exit()
    return pd.DataFrame(rows).set_index("nwsli")


def main():
    """Go Main Go."""
    resp = exponential_backoff(httpx.get, URI, timeout=30)
    if resp is None:
        LOG.info("failed to fetch %s", URI)
        return
    data = resp.json()
    if "features" not in data:
        LOG.info(
            "Got status_code: %s, invalid result of: %s",
            resp.status_code,
            json.dumps(data, sort_keys=True, indent=4, separators=(",", ": ")),
        )
        return
    df = process_features(data["features"])
    pgconn = get_dbconn("iem")
    with get_sqlalchemy_conn("iem") as conn:
        xref = pd.read_sql(
            "SELECT id, nwsli from rwis_locations",
            conn,
            index_col="nwsli",
        )
    df["location_id"] = xref["id"]

    cursor = pgconn.cursor()
    updates = 0
    for nwsli, row in df.iterrows():
        if pd.isnull(nwsli) or pd.isnull(row["location_id"]):
            continue
        location_id = int(row["location_id"])
        cursor.execute(
            "SELECT valid from rwis_soil_data where sensor_id = %s and "
            "location_id = %s",
            (row["sensor_id"], location_id),
        )
        if cursor.rowcount == 0:
            LOG.warning("adding soil entry %s %s", nwsli, row["sensor_id"])
            cursor.execute(
                "INSERT into rwis_soil_data (valid, sensor_id, location_id) "
                "VALUES ('1980-01-01', %s, %s) RETURNING valid",
                (row["sensor_id"], location_id),
            )
        current = cursor.fetchone()[0]
        if row["valid"] <= current:
            continue
        cursor.execute(
            """
            UPDATE rwis_soil_data SET valid = %s, temp = %s, updated = now()
            WHERE sensor_id = %s and location_id = %s
            """,
            (
                row["valid"],
                clean2(row["tmpf"]),
                row["sensor_id"],
                location_id,
            ),
        )
        updates += 1
    LOG.info("updated %s rows", updates)
    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
