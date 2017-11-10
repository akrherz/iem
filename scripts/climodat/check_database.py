"""
 Check over the database and make sure we have what we need there to
 make the climodat reports happy...
"""
from __future__ import print_function
import sys

import mx.DateTime
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
import constants

state = sys.argv[1]
nt = NetworkTable("%sCLIMATE" % (state,))
COOP = get_dbconn('coop')
ccursor = COOP.cursor()

today = mx.DateTime.now()


def fix_year(station, year):
    sts = mx.DateTime.DateTime(year, 1, 1)
    ets = mx.DateTime.DateTime(year+1, 1, 1)
    interval = mx.DateTime.RelativeDateTime(days=1)
    now = sts
    while now < ets:
        ccursor.execute("""SELECT count(*) from alldata_%s where
        station = '%s' and day = '%s' """ % (state, station,
                                             now.strftime("%Y-%m-%d")))
        row = ccursor.fetchone()
        if row[0] == 0:
            print('Adding Date: %s station: %s' % (now, station))
            ccursor.execute("""
                INSERT into alldata_%s (station, day, sday,
                year, month) VALUES ('%s', '%s', '%s', %s, %s)
            """ % (state, station, now.strftime("%Y-%m-%d"),
                   now.strftime("%m%d"), now.year, now.month))
        now += interval


def main():
    """Go Main"""
    for station in nt.sts:
        sts = mx.DateTime.DateTime(constants.startyear(station), 1, 1)
        ets = constants._ENDTS

        # Check for obs total
        now = sts
        interval = mx.DateTime.RelativeDateTime(years=1)
        while now < (ets - interval):
            days = int(((now + interval) - now).days)
            ccursor.execute("""SELECT count(*) from alldata_%s WHERE
            year = %s and station = '%s'""" % (state, now.year, station))
            row = ccursor.fetchone()
            if row[0] != days:
                print ('Mismatch station: %s year: %s count: %s days: %s'
                       '') % (station, now.year, row[0], days)
                fix_year(station, now.year)
            now += interval

        # Check records database...
        sts = mx.DateTime.DateTime(2000, 1, 1)
        ets = mx.DateTime.DateTime(2001, 1, 1)
        interval = mx.DateTime.RelativeDateTime(days=1)
        for table in ['climate', 'climate51', 'climate71', 'climate81']:
            ccursor.execute("""SELECT count(*) from %s WHERE
                station = '%s'""" % (table, station))
            row = ccursor.fetchone()
            if row[0] == 366:
                continue
            now = sts
            while now < ets:
                ccursor.execute("""SELECT * from %s WHERE station = '%s'
                    and valid = '%s'
                    """ % (table, station, now.strftime("%Y-%m-%d")))
                if ccursor.rowcount == 0:
                    print(("Add %s station: %s day: %s"
                           ) % (table, station, now.strftime("%Y-%m-%d")))
                    ccursor.execute("""
                    INSERT into %s (station, valid) values ('%s', '%s')
                    """ % (table, station, now.strftime("%Y-%m-%d")))
                now += interval

    ccursor.close()
    COOP.commit()


if __name__ == '__main__':
    main()
