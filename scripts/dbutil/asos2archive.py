"""
Dump ASOS observations into the long term archive...

This script copies from the iem->current_log database table to the asos
database.  This data is a result of the pyWWA/metar_parser.py process.

The script looks for any updated rows since the last time it ran, this is
tracked in the properties table.

Run from RUN_10MIN.sh
"""
import datetime
import sys

import psycopg2.extras
from pyiem.util import get_dbconn, logger, utc

LOG = logger()
PROPERTY_NAME = "asos2archive_last"
ISO9660 = "%Y-%m-%dT%H:%M:%SZ"


def get_first_updated():
    """Figure out which is the last updated timestamp we ran for."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT propvalue from properties where propname = %s",
        (PROPERTY_NAME,),
    )
    if cursor.rowcount == 0:
        LOG.info("iem property %s is not set, abort!", PROPERTY_NAME)
        sys.exit()

    dt = datetime.datetime.strptime(cursor.fetchone()[0], ISO9660)
    return dt.replace(tzinfo=datetime.timezone.utc)


def set_last_updated(value):
    """Update the database."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "UPDATE properties SET propvalue = %s where propname = %s",
        (value.strftime(ISO9660), PROPERTY_NAME),
    )
    if cursor.rowcount == 0:
        LOG.info("iem property %s did not update, abort!", PROPERTY_NAME)
        sys.exit()

    cursor.close()
    pgconn.commit()


def compute_time(argv):
    """Figure out the proper start and end time"""
    utcnow = utc()
    utcnow = utcnow.replace(minute=0, second=0, microsecond=0)

    if len(argv) == 1:  # noargs
        yesterday = utcnow - datetime.timedelta(hours=24)
        sts = yesterday.replace(hour=0)
        ets = sts.replace(hour=23, minute=59)
    elif len(argv) == 4:
        sts = utc(int(argv[1]), int(argv[2]), int(argv[3]))
        ets = sts.replace(hour=23, minute=59)
    else:
        lasthour = utcnow - datetime.timedelta(minutes=60)
        sts = lasthour.replace(minute=0)
        ets = lasthour.replace(minute=59)
    return sts, ets


def do_insert(source_cursor, madis):
    """Insert the rows into the archive."""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()

    (inserts, skips, deletes) = (0, 0, 0)
    report_type = 1 if madis else 2
    for row in source_cursor:
        # Look for previous entries
        cursor.execute(
            "SELECT metar from alldata where station = %s and valid = %s "
            "and report_type = %s",
            (row["id"], row["valid"], report_type),
        )
        if cursor.rowcount > 0:
            metar = cursor.fetchone()[0]
            if metar == row["raw"]:
                skips += 1
                continue
            # Skip if old metar is longer and new metar is not a COR
            if (
                metar is not None
                and len(metar) > len(row["raw"])
                and row["raw"].find(" COR ") == 0
            ):
                skips += 1
                continue
            cursor.execute(
                "DELETE from alldata where station = %s and valid = %s "
                "and report_type = %s",
                (row["id"], row["valid"], report_type),
            )
            deletes += cursor.rowcount

        sql = """
        INSERT into alldata (station, valid, tmpf,
        dwpf, drct, sknt,  alti, p01i, gust, vsby, skyc1, skyc2, skyc3, skyc4,
        skyl1, skyl2, skyl3, skyl4, metar, p03i, p06i, p24i, max_tmpf_6hr,
        min_tmpf_6hr, max_tmpf_24hr, min_tmpf_24hr, mslp, wxcodes,
        ice_accretion_1hr, ice_accretion_3hr, ice_accretion_6hr,
        report_type, feel, relh, peak_wind_gust, peak_wind_drct,
        peak_wind_time, snowdepth)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
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
            report_type,
            row["feel"],
            row["relh"],
            row["peak_wind_gust"],
            row["peak_wind_drct"],
            row["peak_wind_time"],
            row["snowdepth"],
        )

        cursor.execute(sql, args)
        inserts += 1
        if inserts % 1000 == 0:
            LOG.debug("cycling cursor at %s inserts", inserts)
            cursor.close()
            pgconn.commit()
            cursor = pgconn.cursor()

    LOG.debug("insert %s, skip %s delete %s rows", inserts, skips, deletes)
    cursor.close()
    pgconn.commit()


def main():
    """Do Something Good"""
    last_updated = utc()
    first_updated = get_first_updated()
    iempgconn = get_dbconn("iem")
    icursor = iempgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    LOG.debug(
        "Processing %s thru %s",
        first_updated.strftime(ISO9660),
        last_updated.strftime(ISO9660),
    )

    for madis in [False, True]:
        limiter = "~*" if madis else "!~*"
        # Get obs from access, prioritize observations by if they are a
        # CORrection or not and then their length :?
        # see @akrherz/iem#104 as an enhancement to differentiate rtype
        icursor.execute(
            f"""
            WITH data as (
                SELECT c.*, t.network, t.id, row_number() OVER
                (PARTITION by c.iemid, valid
                ORDER by
                (case when strpos(raw, ' COR ') > 0 then 1 else 0 end) DESC,
                length(raw) DESC) from
                current_log c JOIN stations t on (t.iemid = c.iemid) WHERE
                updated >= %s and updated <= %s and raw {limiter} 'MADISHF'
                and (network ~* 'ASOS' or network = 'AWOS'))
            SELECT * from data where row_number = 1
            """,
            (first_updated, last_updated),
        )
        LOG.debug("processing %s rows for madis: %s", icursor.rowcount, madis)
        if icursor.rowcount > 0:
            do_insert(icursor, madis)

        if icursor.rowcount == 0 and not madis:
            LOG.info(
                "%s - %s Nothing done?",
                first_updated.strftime("%Y-%m-%dT%H:%M"),
                last_updated.strftime("%Y-%m-%dT%H:%M"),
            )
    set_last_updated(last_updated)


if __name__ == "__main__":
    main()
