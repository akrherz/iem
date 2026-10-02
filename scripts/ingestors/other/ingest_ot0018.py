"""ISU Agronomy Hall Vantage Pro 2 OT0018.

Called from RUN_5MIN.sh
"""

import json
from datetime import timedelta

import click
import requests
from metpy.units import units
from pyiem.database import get_dbconnc
from pyiem.observation import Observation
from pyiem.util import get_properties, logger, utc

LOG = logger()


@click.command()
@click.option("--debug", is_flag=True)
def main(debug: bool):
    """Go Main Go"""
    props = get_properties()
    # Query Davis Website
    resp = requests.get(
        f"https://api.weatherlink.com/v2/current/{props['OT0018_station_id']}"
        f"?api-key={props['OT0018_api_key']}",
        headers={
            "User-Agent": "PyIEM",
            "X-Api-Secret": props["OT0018_api_secret"],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if debug:
        print(json.dumps(data, indent=4))

    iem = None
    for sensor in data.get("sensors", []):
        if sensor["data_structure_type"] == 10:
            item = sensor["data"][0]
            iem = Observation(
                "OT0018",
                "OT",
                utc(1970, 1, 1) + timedelta(seconds=int(item["ts"])),
            )
            LOG.info("Found observation for %s", iem.data["valid"])

    if iem is None:
        LOG.warning(
            "Failed to find data_structure_type 10 in %s",
            json.dumps(data, indent=4),
        )
        return

    for sensor in data.get("sensors", []):
        if sensor["sensor_type"] == 242:
            item = sensor["data"][0]
            iem.data["mslp"] = (
                (item["bar_sea_level"] * units("inHg")).to(units("hPa")).m
            )
        if sensor["data_structure_type"] == 10:
            iem.data["relh"] = item["hum"]
            iem.data["dwpf"] = item["dew_point"]
            iem.data["tmpf"] = item["temp"]
            iem.data["sknt"] = (
                (item["wind_speed_last"] * units("mile / hour"))
                .to(units("knot"))
                .m
            )
            iem.data["drct"] = item["wind_dir_last"]
            iem.data["srad"] = item["solar_rad"]
            iem.data["pday"] = item["rainfall_daily_in"]

    iemaccess, cursor = get_dbconnc("iem")
    if not iem.save(cursor):
        LOG.info("iem.save returned false...")
    cursor.close()
    iemaccess.commit()


if __name__ == "__main__":
    main()
