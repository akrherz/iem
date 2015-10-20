"""Compute the Statewide and Climate District Averages!"""
import netCDF4
import psycopg2
import numpy as np
from pyiem import iemre
from pyiem.datatypes import temperature
import sys
import datetime

COOP = psycopg2.connect(database="coop", host='iemdb')
ccursor = COOP.cursor()


def update_database(stid, valid, high, low, precip):
    """Update the database with these newly computed values!"""
    table = "alldata_%s" % (stid[:2], )
    # See if we need to add an entry
    ccursor.execute("""SELECT day from """ + table + """ WHERE day = %s
    and station = %s""", (valid, stid))
    if ccursor.rowcount != 1:
        ccursor.execute("""INSERT into """ + table + """ (station, day,
        high, low, precip, estimated, year, month, sday) VALUES
        (%s, %s, %s, %s, %s, 't', %s, %s, %s)
        """, (stid, valid, high, low, round(precip, 2), valid.year,
              valid.month, valid.strftime("%m%d")))
    # Now we update
    ccursor.execute("""
        UPDATE """ + table + """
        SET high = %s, low = %s, precip = %s
        WHERE station = %s and day = %s
    """, (high, low, round(precip, 2), stid, valid))
    if ccursor.rowcount != 1:
        print('compute_0000:update_database updated %s row for %s %s' % (
            ccursor.rowcount, stid, valid))


def do_day(valid):
    """ Process a day please """
    idx = iemre.daily_offset(valid)
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (valid.year, ),
                         'r')
    high = temperature(nc.variables['high_tmpk_12z'][idx, :, :],
                       'K').value('F')
    low = temperature(nc.variables['low_tmpk_12z'][idx, :, :],
                      'K').value('F')
    precip = nc.variables['p01d_12z'][idx, :, :] / 25.4
    nc.close()
    for state in ('IA', 'NE', 'MN', 'WI', 'MI', 'OH', 'IN', 'IL', 'MO',
                  'KS', 'KY', 'ND', 'SD'):
        do_state_day(state, valid, high, low, precip)
        do_climdiv_day(state, valid, high, low, precip)


def do_climdiv_day(stabbr, valid, highgrid, lowgrid, precipgrid):
    """
    Compute the virtual climate division data as well
    """
    sw_nc = netCDF4.Dataset("/mesonet/data/iemre/climdiv_weights.nc")
    for varname in sw_nc.variables.keys():
        if varname in ['lat', 'lon', 'time']:
            continue
        if varname[:2] != stabbr:
            continue
        stid = varname
        sw = sw_nc.variables[stid][:]

        high = np.average(highgrid[sw > 0])
        low = np.average(lowgrid[sw > 0])
        precip = np.average(precipgrid[sw > 0])

        print(('%s %s-%s-%s High: %5.1f Low: %5.1f Precip: %4.2f'
               ) % (stid, valid.year, valid.month,
                    valid.day, high, low, precip))
        update_database(stid, valid, high, low, precip)

    sw_nc.close()


def do_state_day(stabbr, valid, highgrid, lowgrid, precipgrid):
    """
    Create the statewide average value based on averages of the IEMRE
    """

    # get state weights
    sw_nc = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")
    sw = sw_nc.variables[stabbr][:]
    sw_nc.close()

    high = np.average(highgrid[sw > 0])
    low = np.average(lowgrid[sw > 0])
    precip = np.average(precipgrid[sw > 0])

    print(('%s %s-%s-%s NEW High: %5.1f Low: %5.1f Precip: %4.2f'
           ) % (stabbr, valid.year, valid.month,
                valid.day, high, low, precip))

    update_database(stabbr+"0000", valid, high, low, precip)


def main():
    if len(sys.argv) == 4:
        do_day(datetime.date(int(sys.argv[1]), int(sys.argv[2]),
                             int(sys.argv[3])))
    elif len(sys.argv) == 3:
        sts = datetime.date(int(sys.argv[1]), int(sys.argv[2]), 1)
        ets = sts + datetime.timedelta(days=35)
        ets = ets.replace(day=1)
        now = sts
        while now < ets:
            do_day(now)
            now += datetime.timedelta(days=1)
    else:
        do_day(datetime.date.today())

if __name__ == '__main__':
    main()
    ccursor.close()
    COOP.commit()
