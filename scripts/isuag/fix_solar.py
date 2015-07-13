"""
 Some of our solar radiation data is not good!
"""
import psycopg2
import datetime
ISUAG = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
cursor = ISUAG.cursor()
cursor2 = ISUAG.cursor()


def main():
    """ Go main go """
    cursor.execute("""
     SELECT station, valid from sm_daily where slrmj_tot is null or
     slrmj_tot = 0 and valid > '2015-04-14' ORDER by valid ASC
    """)
    for row in cursor:
        station = row[0]
        v1 = datetime.datetime(row[1].year, row[1].month, row[1].day)
        v2 = v1.replace(hour=23, minute=59)
        cursor2.execute("""
        SELECT sum(slrmj_tot), count(*) from sm_hourly WHERE
        station = %s and valid >= %s and valid < %s
        """, (station, v1, v2))
        row2 = cursor2.fetchone()
        if row2[0] is None:
            print('Double Failure %s %s' % (station, v1.strftime("%d %b %Y")))
            continue
        print('%s %s -> %.2f (%s obs)' % (station, v1.strftime("%d %b %Y"),
                                          row2[0], row2[1]))
        cursor2.execute("""UPDATE sm_daily SET slrmj_tot = %s
        WHERE station = %s and valid = %s""", (row2[0], station, row[1]))

    cursor2.close()
    ISUAG.commit()

if __name__ == '__main__':
    main()
