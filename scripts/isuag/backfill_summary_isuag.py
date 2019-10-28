"""
 Backfill information into the IEM summary table, so the website tools are
 happier
"""
from __future__ import print_function

from pyiem.util import get_dbconn
from pyiem.datatypes import speed

ISUAG = get_dbconn("isuag", user="mesonet")

IEM = get_dbconn("iem", user="mesonet")


def two():
    """option 2"""
    icursor = ISUAG.cursor()
    iemcursor = IEM.cursor()
    icursor.execute(
        """
    SELECT station, date(valid) as dt, min(c200), max(c200), avg(c200)
    from hourly where c200 >= 0 and c200 <= 100 GROUP by station, dt
    """
    )
    for row in icursor:
        station = row[0]
        valid = row[1]
        min_rh = row[2]
        max_rh = row[3]
        avg_rh = row[4]
        iemcursor.execute(
            """
            SELECT min_rh, max_rh, avg_rh from summary s JOIN stations t on
            (t.iemid = s.iemid)
            WHERE day = %s and t.id = %s and t.network = 'ISUAG'
        """,
            (valid, station),
        )
        if iemcursor.rowcount == 0:
            print(
                ("Adding summary_%s row %s %s") % (valid.year, station, valid)
            )
            iemcursor.execute(
                """
            INSERT into summary_"""
                + str(valid.year)
                + """
            (iemid, day) VALUES (
                (SELECT iemid from stations where id = '%s' and
                network = 'ISUAG'), '%s')
            """
                % (station, valid)
            )
            row2 = [None, None, None]
        else:
            row2 = iemcursor.fetchone()
        if (
            row2[1] is None
            or row2[0] is None
            or row2[2] is None
            or round(row2[0], 2) != round(min_rh, 2)
            or round(row2[2], 2) != round(avg_rh, 2)
            or round(row2[1], 2) != round(max_rh, 2)
        ):
            print(
                (
                    "Mismatch %s %s min_rh: %s->%s max_rh: %s->%s "
                    "avg_rh: %s->%s"
                )
                % (
                    station,
                    valid,
                    row2[0],
                    min_rh,
                    row2[1],
                    max_rh,
                    row2[2],
                    avg_rh,
                )
            )

            iemcursor.execute(
                """
            UPDATE summary SET min_rh = %s,
            max_rh = %s, avg_rh = %s WHERE
            iemid = (select iemid from stations WHERE network = 'ISUSM' and
            id = %s) and day = %s
            """,
                (min_rh, max_rh, avg_rh, station, valid),
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
        SELECT station, valid, c11 as high, c12 as low, c90 as pday,
        c40 as avg_mph, c80 * 0.04184 as srad, c20 as avg_rh
        from daily WHERE station != 'A133259' ORDER by valid ASC
    """
    )

    for i, row in enumerate(icursor):
        max_tmpf = row[2]
        min_tmpf = row[3]
        pday = row[4]
        avg_sknt = speed(row[5], "MPH").value("KT")
        srad = row[6]
        avg_rh = row[7]

        def myfunc():
            iemcursor.execute(
                """
            UPDATE summary SET avg_sknt = %s, max_tmpf = %s, min_tmpf = %s,
            srad_mj = %s, pday = %s, avg_rh = %s
            WHERE
            iemid = (select iemid from stations WHERE network = 'ISUAG' and
            id = %s) and day = %s
            """,
                (
                    avg_sknt,
                    max_tmpf,
                    min_tmpf,
                    srad,
                    pday,
                    avg_rh,
                    row[0],
                    row[1],
                ),
            )

        myfunc()
        if iemcursor.rowcount != 1:
            print("update %s %s did not work" % (row[0], row[1]))
            iemcursor.execute(
                """
            INSERT into summary_"""
                + str(row[1].year)
                + """ (iemid, day)
            VALUES ((select iemid from stations where id = %s and
                    network = 'ISUAG'), %s)
            """,
                (row[0], row[1]),
            )
            myfunc()
        if i % 1000 == 0:
            iemcursor.close()
            IEM.commit()
            iemcursor = IEM.cursor()
        i += 1
    iemcursor.close()
    IEM.commit()
    IEM.close()


def main():
    """Go Main Go"""
    one()


if __name__ == "__main__":
    main()
