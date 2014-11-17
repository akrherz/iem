import psycopg2
import datetime
import sys
from pyiem.network import Table as NetworkTable

PGCONN = psycopg2.connect(database='coop', host='iemdb')
cursor = PGCONN.cursor()

def main():
    """ Go Main Go """
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    sts = datetime.datetime(year, month, 1)
    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)
    nt = NetworkTable("IACLIMATE")
    for sid in nt.sts.keys():
        if sid[2] == 'C' or sid == 'IA0000':
            continue
        cursor.execute("""SELECT count(*) from alldata_ia where 
        station = %s and month = %s and year = %s""", (sid, month, year))
        row = cursor.fetchone()
        if row[0] == 0:
            now = sts
            while now < ets:
                print "Adding %s %s" % (sid, now.strftime("%d %b %Y"))
                cursor.execute("""INSERT into alldata_ia(station, day, year,
                month, sday)
                VALUES (%s, %s, %s, %s, %s)""", (sid, now, now.year,
                                            now.month, now.strftime("%m%d")))
                now += datetime.timedelta(days=1)
            

if __name__ == '__main__':
    main()
    cursor.close()
    PGCONN.commit()
    PGCONN.close()