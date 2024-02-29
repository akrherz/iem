"""Ingest the El Nino"""

import datetime

import pandas as pd
import requests
from pyiem.util import get_dbconnc, get_sqlalchemy_conn


def main():
    """Go Main Go"""
    mesosite, mcursor = get_dbconnc("coop")

    # Get max date
    with get_sqlalchemy_conn("coop") as engine:
        current = pd.read_sql(
            "SELECT monthdate, anom_34, soi_3m from elnino",
            engine,
            index_col="monthdate",
        )

    url = "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices"
    data = requests.get(url, timeout=30).content.decode("ascii").split("\n")

    for line in data[1:]:
        tokens = line.split()
        if len(tokens) < 3:
            continue
        anom34 = float(tokens[-1])
        date = datetime.date(int(tokens[0]), int(tokens[1]), 1)
        if date in current.index:
            if current.loc[date]["anom_34"] != anom34:
                print(
                    f"anom_34 update {date.year}-{date.month}-01: "
                    f"{current.loc[date]['anom_34']} -> {anom34}"
                )
                mcursor.execute(
                    "UPDATE elnino SET anom_34 = %s WHERE monthdate = %s",
                    (anom34, date),
                )
            continue
        print(f"Found ElNino3.4! {date} {anom34}")
        # Add entry to current dataframe
        current.loc[date] = [anom34, None]
        mcursor.execute(
            "INSERT into elnino(monthdate, anom_34) values (%s, %s)",
            (date, anom34),
        )

    url = "https://www.cpc.ncep.noaa.gov/data/indices/soi.3m.txt"
    data = requests.get(url, timeout=30).content.decode("ascii").split("\n")

    for line in data[1:]:
        if len(line) < 3:
            continue
        year = int(line[:4])
        pos = 4
        for month in range(1, 13):
            soi = float(line[pos : pos + 6])
            pos += 6
            date = datetime.date(year, month, 1)
            if soi < -999:
                continue
            if date in current.index:
                if current.loc[date]["soi_3m"] != soi:
                    print(
                        f"soi_3m update {date.year}-{date.month}-01: "
                        f"{current.loc[date]['soi_3m']} -> {soi}"
                    )
                    mcursor.execute(
                        "UPDATE elnino SET soi_3m = %s WHERE monthdate = %s",
                        (soi, date),
                    )
                continue
            mcursor.execute(
                "INSERT into elnino(monthdate, soi_3m) values (%s, %s)",
                (date, soi),
            )

    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main()
