"""
My purpose in life is to sync the mesosite stations table to other
databases.  This will hopefully remove some hackery
"""

import numpy as np
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.util import logger, utc

LOG = logger()


def sync(df, dbname):
    """
    Actually do the syncing, please
    """
    # connect to synced database
    dbconn, dbcursor = get_dbconnc(dbname)
    # Figure out our latest revision
    dbcursor.execute(
        "SELECT max(modified) as mm, max(iemid) as mi from stations"
    )
    row = dbcursor.fetchone()
    maxts = row["mm"] or utc(1980, 1, 1)
    maxid = row["mi"] or -1
    # Check for stations that were removed from mesosite
    with get_sqlalchemy_conn(dbname) as conn:
        localdf = pd.read_sql(
            "SELECT iemid, modified from stations ORDER by iemid ASC",
            conn,
            index_col="iemid",
        )
    localdf["iemid"] = localdf.index.values
    todelete = localdf.index.difference(df.index)
    if not todelete.empty:
        for iemid in todelete.values:
            dbcursor.execute(
                "DELETE from stations where iemid = %s",
                (iemid,),
            )
        dbcursor.close()
        dbconn.commit()
        dbcursor = dbconn.cursor()

    changes = df[(df["iemid"] > maxid) | (df["modified"] > maxts)]
    for _iemid, row in changes.iterrows():
        prow = row.replace({np.nan: None}).to_dict()
        if prow["iemid"] not in localdf.index:
            dbcursor.execute(
                "INSERT into stations(iemid, network, id) VALUES(%s, %s, %s)",
                (prow["iemid"], prow["network"], prow["id"]),
            )

        # insert queried stations
        dbcursor.execute(
            """
            UPDATE stations SET name = %(name)s,
            state = %(state)s, elevation = %(elevation)s, online = %(online)s,
            geom = %(geom)s, params = %(params)s, county = %(county)s,
            plot_name = %(plot_name)s, climate_site = %(climate_site)s,
            wfo = %(wfo)s, archive_begin = %(archive_begin)s,
            archive_end = %(archive_end)s, remote_id = %(remote_id)s,
            tzname = %(tzname)s, country = %(country)s,
            modified = %(modified)s, network = %(network)s,
            metasite = %(metasite)s,
            sigstage_low = %(sigstage_low)s,
            sigstage_action = %(sigstage_action)s,
            sigstage_bankfull = %(sigstage_bankfull)s,
            sigstage_flood = %(sigstage_flood)s,
            sigstage_moderate = %(sigstage_moderate)s,
            sigstage_major = %(sigstage_major)s,
            sigstage_record = %(sigstage_record)s, ugc_county = %(ugc_county)s,
            ugc_zone = %(ugc_zone)s, id = %(id)s, ncdc81 = %(ncdc81)s,
            ncei91 = %(ncei91)s,
            temp24_hour = %(temp24_hour)s, precip24_hour = %(precip24_hour)s,
            wigos = %(wigos)s
            WHERE iemid = %(iemid)s
       """,
            prow,
        )
    LOG.info(
        "DB: %-7s Del %3s Mod %4s rows TS: %s IEMID: %s",
        dbname,
        len(todelete),
        len(changes.index),
        maxts.strftime("%Y/%m/%d %H:%M"),
        maxid,
    )
    dbcursor.close()
    dbconn.commit()
    # close connection
    dbconn.close()


def main():
    """Go Main Go"""
    subscribers = (
        "iem isuag coop hads hml asos asos1min postgis raob"
    ).split()

    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            "SELECT * from stations ORDER by iemid ASC",
            conn,
            index_col="iemid",
        )
    df["iemid"] = df.index.values
    # fix dtype for two columns
    for col in ["temp24_hour", "precip24_hour", "remote_id"]:
        df[col] = df[col].astype("Int64")
    for sub in subscribers:
        sync(df, sub)


if __name__ == "__main__":
    main()
