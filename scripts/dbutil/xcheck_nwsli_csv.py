"""See if we have metadata in a local CSV file

NOTE: I had to manually edit the .csv file to remove the first row
"""
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

CSVFN = "/home/akrherz/Downloads/nwsli_database.csv"


def dowork(df, nwsli):
    """do work!"""
    df2 = df[df["NWSLI"] == nwsli]
    if df2.empty:
        return
    row = df2.iloc[0]
    print("------")
    print(row["NWSLI"])
    print(
        "%s %s%s - %s"
        % (row["City"], row["Detail"], row["Direction"], row["Station Name"])
    )
    print(row["State"])
    print(f"Program {row['Program']}")
    print(row["Latitude"])
    print(row["Longitude"])


def main():
    """Go Main Go!"""
    pgconn = get_dbconn("hads", user="mesonet")
    udf = read_sql(
        "SELECT distinct nwsli, 1 as col from unknown ORDER by nwsli",
        pgconn,
        index_col="nwsli",
    )
    print("Found %s unknown entries" % (len(udf.index),))
    df = pd.read_csv(CSVFN, low_memory=False)
    for nwsli, _row in udf.iterrows():
        dowork(df, nwsli)


if __name__ == "__main__":
    main()
