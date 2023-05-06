"""Ingest Iowa DOT RWIS data provided by DTN."""

# third party
import numpy as np
import pandas as pd
import requests
from metpy.units import masked_array, units
from pyiem.network import Table as NetworkTable
from pyiem.observation import Observation
from pyiem.util import get_dbconn, get_properties, logger, utc

LOG = logger()
DBCONN = get_dbconn("iem")
NT = NetworkTable("IA_RWIS")


def process(cursor, df, nwsli):
    """Process our data."""
    for _, row in df.iterrows():
        ob = Observation(nwsli, "IA_RWIS", row["valid"])
        ob.data["tmpf"] = row["temperature"]
        ob.data["dwpf"] = row["dewPoint"]
        ob.data["relh"] = row["relativeHumidity"]
        ob.data["vsby"] = row["visibility"]
        ob.data["drct"] = row["windDirection"]
        ob.data["gust"] = row["gust"]
        ob.data["sknt"] = row["sknt"]
        ob.save(cursor, force_current_log=True)


def main():
    """Go Main Go."""
    # prevent a clock drift issue
    sts = utc(2020, 8, 10, 16)
    ets = utc(2020, 8, 11, 3)
    edate = ets.strftime("%Y-%m-%dT%H:%M:%SZ")
    sdate = sts.strftime("%Y-%m-%dT%H:%M:%SZ")
    props = get_properties()
    apikey = props["dtn.apikey"]
    headers = {"accept": "application/json", "apikey": apikey}
    for nwsli in NT.sts:
        idot_id = NT.sts[nwsli]["remote_id"]
        if idot_id is None:
            continue
        URI = (
            f"https://api.dtn.com/weather/stations/IA{idot_id:03}/"
            f"atmospheric-observations?startDate={sdate}"
            f"&endDate={edate}&units=us&precision=0"
        )

        req = requests.get(URI, timeout=60, headers=headers)
        if req.status_code != 200:
            LOG.info("Fetch %s got status_code %s", URI, req.status_code)
            continue
        res = req.json()
        if not res:
            continue
        try:
            df = pd.DataFrame(res)
        except Exception as exp:
            LOG.info(
                "DataFrame construction failed with %s\n res: %s", exp, res
            )
            continue
        if df.empty:
            continue
        df = df.fillna(np.nan)
        df["valid"] = pd.to_datetime(df["utcTime"])
        df["gust"] = (
            masked_array(df["windGust"].values, units("miles per hour"))
            .to(units("knots"))
            .m
        )
        df["sknt"] = (
            masked_array(df["windSpeed"].values, units("miles per hour"))
            .to(units("knots"))
            .m
        )
        df = df.replace({np.nan: None})
        cursor = DBCONN.cursor()
        process(cursor, df, nwsli)
        cursor.close()
        DBCONN.commit()


if __name__ == "__main__":
    main()
