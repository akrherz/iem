"""Ingest what NCEI has for its climdiv dataset.

Run from RUN_0Z.sh
"""

import pandas as pd
import requests
from pyiem.reference import ncei_state_codes
from pyiem.util import get_dbconn, get_properties, logger, set_property

LOG = logger()
ELEMENT2IEM = {
    "pcpn": "precip",
    "tmin": "low",
    "tmax": "high",
}


def process(procdate, region):
    """Process the climdiv data."""
    ncei2state = {}
    for key, val in ncei_state_codes.items():
        if region == "st":
            ncei2state[f"{int(val):03.0f}"] = key
        else:
            ncei2state[f"{int(val):02.0f}"] = key
    alldf = None
    pos = 3 if region == "st" else 2
    for element, iemvar in ELEMENT2IEM.items():
        LOG.info("Fetching %s[%s]", element, region)
        df = (
            pd.read_csv(
                "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/"
                f"climdiv-{element}{region}-v1.0.0-{procdate}",
                names="stcode 1 2 3 4 5 6 7 8 9 10 11 12".split(),
                dtype={"stcode": str},
                sep=r"\s+",
                na_values=["-9.99", "-99.90"],
            )
            .assign(
                state=lambda df_: df_["stcode"].str.slice(0, pos),
                divnum=lambda df_: df_["stcode"].str.slice(pos, 4),
                year=lambda df_: pd.to_numeric(df_["stcode"].str.slice(6, 10)),
            )
            .assign(
                state=lambda df_: df_["state"].map(ncei2state),
                station=lambda df_: (
                    df_["state"]
                    + ("" if region == "st" else "C")
                    + df_["divnum"].str.pad(
                        4 if region == "st" else 3, fillchar="0"
                    )
                ),
            )
            .dropna(subset=["state"])
            .drop(columns=["stcode", "state", "divnum"])
            .melt(
                id_vars=["station", "year"],
                value_vars="1 2 3 4 5 6 7 8 9 10 11 12".split(),
                var_name="month",
                value_name=iemvar,
            )
            .assign(
                day=1,
                date=lambda df_: pd.to_datetime(df_[["year", "month", "day"]]),
            )
            .drop(columns=["year", "month", "day"])
            .set_index(["station", "date"])
            .dropna()
        )
        if alldf is None:
            alldf = df
        else:
            alldf[iemvar] = df[iemvar]
    return alldf.reset_index()


def update(cursor, row) -> int:
    """Do update."""
    cursor.execute(
        """
        update ncei_climdiv SET precip = %s, high = %s, low = %s
        WHERE station = %s and day = %s
        """,
        (
            row["precip"],
            row["high"],
            row["low"],
            row["station"],
            row["date"],
        ),
    )
    return cursor.rowcount


def dbsave(df):
    """Upsert data into database."""
    conn = get_dbconn("coop")
    cursor = conn.cursor()
    for _, row in df.iterrows():
        if update(cursor, row) != 1:
            cursor.execute(
                "INSERT into ncei_climdiv(station, day) VALUES (%s, %s)",
                (row["station"], row["date"]),
            )
            update(cursor, row)

    cursor.close()
    conn.commit()


def main():
    """Go Main Go."""
    procdate = requests.get(
        "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/procdate.txt",
        timeout=30,
    ).text.strip()
    iemprocdate = get_properties().get("ncei.climdiv.procdate")
    if iemprocdate is not None and iemprocdate == procdate:
        LOG.info("Nothing to do, procdate %s", procdate)
        return
    LOG.warning("Found new %s to process", procdate)
    for region in ["dv", "st"]:
        df = process(procdate, region)
        dbsave(df)
    set_property("ncei.climdiv.procdate", procdate)


if __name__ == "__main__":
    main()
