"""
 Backfill information into the IEM summary table, so the website tools are
 happier
"""

from pyiem.util import get_dbconn, logger, convert_value, c2f

LOG = logger()
ISUAG = get_dbconn("isuag", user="mesonet")
IEM = get_dbconn("iem", user="mesonet")


def two():
    """option 2"""
    icursor = ISUAG.cursor()
    iemcursor = IEM.cursor()
    icursor.execute(
        """
    SELECT station, date(valid) as dt, min(rh), max(rh) from sm_hourly
    where rh >= 0 and rh <= 100 GROUP by station, dt
    """
    )
    for row in icursor:
        station = row[0]
        valid = row[1]
        min_rh = row[2]
        max_rh = row[3]
        iemcursor.execute(
            """
            SELECT min_rh, max_rh from summary s JOIN stations t on
            (t.iemid = s.iemid)
            WHERE day = %s and t.id = %s and t.network = 'ISUSM'
        """,
            (valid, station),
        )
        if iemcursor.rowcount == 0:
            LOG.info("Adding summary_%s row %s %s", valid.year, station, valid)
            iemcursor.execute(
                """
            INSERT into summary_"""
                + str(valid.year)
                + """
            (iemid, day) VALUES (
                (SELECT iemid from stations where id = '%s' and
                network = 'ISUSM'), '%s')
            """
                % (station, valid)
            )
            row2 = [None, None]
        else:
            row2 = iemcursor.fetchone()
        if (
            row2[1] is None
            or row2[0] is None
            or round(row2[0], 2) != round(min_rh, 2)
            or round(row2[1], 2) != round(max_rh, 2)
        ):
            LOG.info(
                "Mismatch %s %s min_rh: %s->%s max_rh: %s->%s",
                station,
                valid,
                row2[0],
                min_rh,
                row2[1],
                max_rh,
            )

            iemcursor.execute(
                """
            UPDATE summary SET min_rh = %s,
            max_rh = %s WHERE
            iemid = (select iemid from stations WHERE network = 'ISUSM' and
            id = %s) and day = %s
            """,
                (min_rh, max_rh, station, valid),
            )
    iemcursor.close()
    IEM.commit()
    IEM.close()


def one():
    """option 1"""
    icursor = ISUAG.cursor()
    iemcursor = IEM.cursor()
    icursor.execute(
        """
        SELECT station, valid, ws_mps_s_wvt, winddir_d1_wvt, rain_in_tot,
        tair_c_max, tair_c_min
        from sm_daily
    """
    )

    for row in icursor:
        avg_sknt = convert_value(row[2], "meter / second", "knot")
        avg_drct = row[3]
        pday = row[4]
        high = c2f(row[5])
        low = c2f(row[6])
        iemcursor.execute(
            """
        UPDATE summary SET avg_sknt = %s, vector_avg_drct = %s, pday = %s,
        max_tmpf = %s, min_tmpf = %s
        WHERE
        iemid = (select iemid from stations WHERE network = 'ISUSM' and
        id = %s) and day = %s
        """,
            (avg_sknt, avg_drct, pday, high, low, row[0], row[1]),
        )
    iemcursor.close()
    IEM.commit()
    IEM.close()


def main():
    """Go Main Go"""
    # one()
    two()


if __name__ == "__main__":
    main()
