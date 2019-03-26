"""See if we have metadata in a local CSV file

NOTE: I had to manually edit the .csv file to remove the first row
"""
from __future__ import print_function

import pandas as pd
from pyiem.util import get_dbconn


def dowork(df, nwsli):
    """do work!"""
    if nwsli not in df['NWSLI'].values:
        # print("Missing %s" % (nwsli, ))
        return
    row = df[df['NWSLI'] == nwsli].iloc[0]
    print("------")
    print(row['NWSLI'])
    print("%s %s%s - %s" % (row['City'], row['Mileage'], row['Direction'],
                            row['Station Name']))
    print(row['State'])
    print(row['Program Acronym'])
    print(row['Latitude'])
    print(row['Longitude'])


def main():
    """Go Main Go!"""
    pgconn = get_dbconn('hads', user='mesonet')
    cursor = pgconn.cursor()
    cursor.execute("""
        SELECT distinct nwsli from unknown ORDER by nwsli
    """)
    df = pd.read_csv('/tmp/nwsli_database.csv', low_memory=False)
    for row in cursor:
        dowork(df, row[0])


if __name__ == '__main__':
    main()
