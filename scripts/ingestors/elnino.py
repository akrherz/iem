"""Ingest the El Nino"""

from datetime import date

import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn


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
    data = httpx.get(url, timeout=30).content.decode("ascii").split("\n")

    for line in data[1:]:
        tokens = line.split()
        if len(tokens) < 3:
            continue
        anom34 = float(tokens[-1])
        dt = date(int(tokens[0]), int(tokens[1]), 1)
        if dt in current.index:
            if current.loc[dt]["anom_34"] != anom34:
                print(
                    f"anom_34 update {dt.year}-{dt.month}-01: "
                    f"{current.loc[dt]['anom_34']} -> {anom34}"
                )
                mcursor.execute(
                    "UPDATE elnino SET anom_34 = %s WHERE monthdate = %s",
                    (anom34, dt),
                )
            continue
        print(f"Found ElNino3.4! {dt} {anom34}")
        # Add entry to current dataframe
        current.at[dt, "anom_34"] = anom34
        current.at[dt, "soi_3m"] = None
        mcursor.execute(
            "INSERT into elnino(monthdate, anom_34) values (%s, %s)",
            (dt, anom34),
        )

    url = "https://www.cpc.ncep.noaa.gov/data/indices/soi.3m.txt"
    data = httpx.get(url, timeout=30).content.decode("ascii").split("\n")

    for line in data[1:]:
        if len(line) < 3:
            continue
        year = int(line[:4])
        pos = 4
        for month in range(1, 13):
            soi = float(line[pos : pos + 6])
            pos += 6
            dt = date(year, month, 1)
            if soi < -999:
                continue
            if dt in current.index:
                if current.loc[dt]["soi_3m"] != soi:
                    print(
                        f"soi_3m update {dt.year}-{dt.month}-01: "
                        f"{current.loc[dt]['soi_3m']} -> {soi}"
                    )
                    mcursor.execute(
                        "UPDATE elnino SET soi_3m = %s WHERE monthdate = %s",
                        (soi, dt),
                    )
                continue
            mcursor.execute(
                "INSERT into elnino(monthdate, soi_3m) values (%s, %s)",
                (dt, soi),
            )

    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main()
