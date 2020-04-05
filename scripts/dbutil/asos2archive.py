"""
 Dump ASOS observations into the long term archive...

 Database partitioning is now based on the UTC day, so we need to make sure
 we are not inserting where we should not be...

 This script copies from the iem->current_log database table to the asos
 database.  This data is a result of the pyWWA/metar_parser.py process

 We run in two modes, once every hour to copy over the past hour's data and
 then once at midnight to recopy the previous day's data.

 RUN_20_AFTER.sh
 RUN_MIDNIGHT.sh

"""
import datetime
import sys

import pytz
import psycopg2.extras
from pyiem.util import get_dbconn, logger

LOG = logger()


def compute_time(is_hourly):
    """Figure out the proper start and end time"""
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    utcnow = utcnow.replace(minute=0, second=0, microsecond=0)

    if is_hourly:
        lasthour = utcnow - datetime.timedelta(minutes=60)
        sts = lasthour.replace(minute=0)
        ets = lasthour.replace(minute=59)
    else:
        yesterday = utcnow - datetime.timedelta(hours=24)
        sts = yesterday.replace(hour=0)
        ets = sts.replace(hour=23, minute=59)
    return sts, ets


def main(argv):
    """Do Something Good"""
    asospgconn = get_dbconn("asos")
    iempgconn = get_dbconn("iem")
    acursor = asospgconn.cursor()
    icursor = iempgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    is_hourly = len(argv) > 1

    (sts, ets) = compute_time(is_hourly)
    LOG.debug(
        "Processing %s thru %s",
        sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        ets.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    # Delete any duplicate obs
    table = "t%s" % (sts.year,)
    acursor.execute(
        """
        DELETE from """
        + table
        + """ WHERE valid >= %s and valid <= %s
        """,
        (sts, ets),
    )

    # Get obs from Access
    icursor.execute(
        """
        WITH data as (
            SELECT c.*, t.network, t.id, row_number() OVER
            (PARTITION by c.iemid, valid ORDER by length(raw) DESC) from
            current_log c JOIN stations t on (t.iemid = c.iemid) WHERE
            valid >= %s and valid <= %s and
            (network ~* 'ASOS' or network = 'AWOS'))
        SELECT * from data where row_number = 1
        """,
        (sts, ets),
    )
    for row in icursor:
        sql = (
            """INSERT into t"""
            + repr(sts.year)
            + """ (station, valid, tmpf,
        dwpf, drct, sknt,  alti, p01i, gust, vsby, skyc1, skyc2, skyc3, skyc4,
        skyl1, skyl2, skyl3, skyl4, metar, p03i, p06i, p24i, max_tmpf_6hr,
        min_tmpf_6hr, max_tmpf_24hr, min_tmpf_24hr, mslp, wxcodes,
        ice_accretion_1hr, ice_accretion_3hr, ice_accretion_6hr,
        report_type, feel, relh, peak_wind_gust, peak_wind_drct,
        peak_wind_time)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        )

        # see @akrherz/iem#104 as an enhancement to differentiate rtype
        rtype = (
            1
            if row["raw"] is not None and row["raw"].find(" MADISHF") > -1
            else 2
        )
        args = (
            row["id"],
            row["valid"],
            row["tmpf"],
            row["dwpf"],
            row["drct"],
            row["sknt"],
            row["alti"],
            row["phour"],
            row["gust"],
            row["vsby"],
            row["skyc1"],
            row["skyc2"],
            row["skyc3"],
            row["skyc4"],
            row["skyl1"],
            row["skyl2"],
            row["skyl3"],
            row["skyl4"],
            row["raw"],
            row["p03i"],
            row["p06i"],
            row["p24i"],
            row["max_tmpf_6hr"],
            row["min_tmpf_6hr"],
            row["max_tmpf_24hr"],
            row["min_tmpf_24hr"],
            row["mslp"],
            row["wxcodes"],
            row["ice_accretion_1hr"],
            row["ice_accretion_3hr"],
            row["ice_accretion_6hr"],
            rtype,
            row["feel"],
            row["relh"],
            row["peak_wind_gust"],
            row["peak_wind_drct"],
            row["peak_wind_time"],
        )

        acursor.execute(sql, args)

    if icursor.rowcount == 0:
        LOG.info(
            "%s - %s Nothing done?",
            sts.strftime("%Y-%m-%dT%H:%M"),
            ets.strftime("%Y-%m-%dT%H:%M"),
        )

    icursor.close()
    iempgconn.commit()
    asospgconn.commit()
    asospgconn.close()
    iempgconn.close()


if __name__ == "__main__":
    main(sys.argv)
