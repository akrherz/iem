"""Look to see if we have something systematic wrong with IEMRE"""
import json
import sys

import requests
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn
from pyiem.network import Table as NetworkTable

COLS = ["ob_pday", "daily_precip_in", "precip_delta", "prism_precip_in"]


def main(argv):
    """Go Main Go"""
    station = argv[1]
    year = int(argv[2])
    pgconn = get_dbconn("coop")

    nt = NetworkTable("IACLIMATE")

    df = read_sql(
        """
        SELECT day, precip, high, low from alldata_ia
        WHERE station = %s and year = %s
        ORDER by day ASC
    """,
        pgconn,
        params=(station, year),
        index_col="day",
    )

    uri = (
        "https://mesonet.agron.iastate.edu/iemre/multiday/%s-01-01/"
        "%s-12-31/%.2f/%.2f/json"
    ) % (year, year, nt.sts[station]["lat"], nt.sts[station]["lon"])
    req = requests.get(uri)
    j = json.loads(req.content)

    idf = pd.DataFrame(j["data"])
    idf["day"] = pd.to_datetime(idf["date"])
    idf.set_index("day", inplace=True)

    idf["ob_high"] = df["high"]
    idf["ob_low"] = df["low"]
    idf["ob_pday"] = df["precip"]

    idf["high_delta"] = idf["ob_high"] - idf["daily_high_f"]
    idf["low_delta"] = idf["ob_low"] - idf["daily_low_f"]
    idf["precip_delta"] = idf["ob_pday"] - idf["daily_precip_in"]
    idf.sort_values("precip_delta", inplace=True, ascending=True)

    print("IEMRE greater than Obs")
    print(idf[COLS].head())
    print("Obs greater than IEMRE")
    print(idf[COLS].tail())
    print("Largest Obs with IEMRE < 0.01")
    idf2 = idf[idf["daily_precip_in"] < 0.01]
    print(idf2[["ob_pday", "daily_precip_in", "precip_delta"]].tail())

    print("Monthly Totals")
    print(idf[COLS].groupby(pd.Grouper(freq="M")).sum())
    print("sum")
    print(idf[COLS].sum())


if __name__ == "__main__":
    main(sys.argv)
