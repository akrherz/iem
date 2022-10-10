"""
 My purpose in life is to sync the mesosite stations table to other
databases.  This will hopefully remove some hackery
"""
import sys

import numpy as np
from pyiem.util import get_dbconn, get_dbconnstr, logger, utc
from pandas import read_sql

LOG = logger()


def sync(df, dbname):
    """
    Actually do the syncing, please
    """
    # connect to synced database
    dbconn = get_dbconn(dbname)
    dbcursor = dbconn.cursor()
    # Figure out our latest revision
    dbcursor.execute("SELECT max(modified), max(iemid) from stations")
    row = dbcursor.fetchone()
    maxts = row[0] or utc(1980, 1, 1)
    maxid = row[1] or -1
    # Check for stations that were removed from mesosite
    localdf = read_sql(
        "SELECT iemid, modified from stations ORDER by iemid ASC",
        get_dbconnstr(dbname),
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
    for iemid, row in changes.iterrows():
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
            temp24_hour = %(temp24_hour)s, precip24_hour = %(precip24_hour)s
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


def main(argv):
    """Go Main Go"""
    mesosite = get_dbconnstr("mesosite")
    subscribers = (
        "iem isuag coop hads hml asos asos1min postgis raob"
    ).split()

    if len(argv) == 3:
        LOG.info(
            "Running laptop syncing from upstream, assume iemdb is localhost!"
        )
        # HACK
        mesosite = get_dbconnstr("mesosite", host="172.16.172.1")
        subscribers.insert(0, "mesosite")
    df = read_sql(
        "SELECT * from stations ORDER by iemid ASC",
        mesosite,
        index_col="iemid",
    )
    df["iemid"] = df.index.values
    for sub in subscribers:
        sync(df, sub)


if __name__ == "__main__":
    main(sys.argv)
