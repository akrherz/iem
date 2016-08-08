"""
 Backfill information into the IEM summary table, so the website tools are
 happier
"""
import psycopg2
from pyiem.datatypes import temperature, distance

ISUAG = psycopg2.connect(database='isuag', host='iemdb')
icursor = ISUAG.cursor()

IEM = psycopg2.connect(database='iem', host='iemdb')
iemcursor = IEM.cursor()


def two():
    icursor.execute("""
    SELECT station, date(valid) as dt, min(rh), max(rh) from sm_hourly
    where rh >= 0 and rh <= 100 GROUP by station, dt
    """)
    for row in icursor:
        station = row[0]
        valid = row[1]
        min_rh = row[2]
        max_rh = row[3]
        iemcursor.execute("""
            SELECT min_rh, max_rh from summary s JOIN stations t on
            (t.iemid = s.iemid)
            WHERE day = %s and t.id = %s and t.network = 'ISUSM'
        """, (valid, station))
        if iemcursor.rowcount == 0:
            print(('Adding summary_%s row %s %s'
                   ) % (valid.year, station, valid))
            iemcursor.execute("""
            INSERT into summary_""" + str(valid.year) + """
            (iemid, day) VALUES (
                (SELECT iemid from stations where id = '%s' and
                network = 'ISUSM'), '%s')
            """ % (station, valid))
            row2 = [None, None]
        else:
            row2 = iemcursor.fetchone()
        if (row2[1] is None or row2[0] is None or
                round(row2[0], 2) != round(min_rh, 2) or
                round(row2[1], 2) != round(max_rh, 2)):
            print(('Mismatch %s %s min_rh: %s->%s max_rh: %s->%s'
                   ) % (station, valid, row2[0], min_rh, row2[1], max_rh))

            iemcursor.execute("""
            UPDATE summary SET min_rh = %s,
            max_rh = %s WHERE
            iemid = (select iemid from stations WHERE network = 'ISUSM' and
            id = %s) and day = %s
            """, (min_rh, max_rh, station, valid))


def one():
    icursor.execute("""SELECT station, valid, rain_mm_tot, tair_c_max,
        tair_c_min from sm_daily WHERE tair_c_max is not null""")

    for row in icursor:
        high = temperature(row[3], 'C').value('F')
        low = temperature(row[4], 'C').value('F')

        iemcursor.execute("""
        SELECT pday, max_tmpf, min_tmpf from summary s JOIN stations t on
        (t.iemid = s.iemid)
        WHERE day = %s and t.id = %s and t.network = 'ISUSM'
        """, (row[1], row[0]))
        if iemcursor.rowcount == 0:
            print 'Adding summary_%s row %s %s' % (row[1].year, row[0], row[1])
            iemcursor.execute("""
            INSERT into summary_""" + str(row[1].year) + """
            (iemid, day, pday, max_tmpf, min_tmpf) VALUES (
                (SELECT iemid from stations where id = '%s' and
                network = 'ISUSM'), '%s', %s, %s, %s)
            """ % (row[0], row[1], distance(row[2], 'MM').value('IN'), high,
                   low))
        else:
            row2 = iemcursor.fetchone()
            if (row2[1] is None or row2[2] is None or
                    round(row2[0], 2) != round((distance(row[2],
                                                         'MM').value('IN')),
                                               2) or
                    round(high, 2) != round(row2[1], 2) or
                    round(low, 2) != round(row2[2], 2)):
                print(('Mismatch %s %s old: %s new: %s'
                       ) % (row[0], row[1], row2[0],
                            distance(row[2], 'MM').value('IN')))

                iemcursor.execute("""
                UPDATE summary SET pday = %s, max_tmpf = %s,
                min_tmpf = %s WHERE
                iemid = (select iemid from stations WHERE network = 'ISUSM' and
                id = %s) and day = %s
                """, (distance(row[2], 'MM').value('IN'), high, low, row[0],
                      row[1]))

two()
iemcursor.close()
IEM.commit()
IEM.close()
