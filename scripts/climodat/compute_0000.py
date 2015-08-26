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


def do_day(valid):
    """ Process a day please """
    idx = iemre.daily_offset(valid)
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (valid.year, ),
                         'r')
    high = temperature(nc.variables['high_tmpk'][idx, :, :], 'K').value('F')
    low = temperature(nc.variables['low_tmpk'][idx, :, :], 'K').value('F')
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

        # Now we insert into the proper database!
        ccursor.execute("""
            DELETE from alldata_""" + stabbr + """
            WHERE station = %s and day = %s""", (stid, valid))

        ccursor.execute("""
            INSERT into alldata_"""+stabbr+"""
            (station, day, high, low, precip, estimated,
            year, month, sday)
            VALUES ('%s', '%s', %.0f, %.0f, %.2f, true, '%s',
            '%s', '%s')
        """ % (stid, valid, high, low, precip, valid.year,
               valid.month, "%02i%02i" % (valid.month, valid.day)))

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

    # Now we insert into the proper database!
    ccursor.execute("""
        DELETE from alldata_""" + stabbr + """
        WHERE station = %s and day = %s""", (stabbr + "0000", valid))
    ccursor.execute("""
        INSERT into alldata_""" + stabbr + """
        (station, day, high, low, precip, estimated,
        year, month, sday)
        VALUES ('%s', '%s', %.0f, %.0f, %.2f, true, '%s',
        '%s', '%s')
    """ % (stabbr + "0000", valid, high, low, precip,
           valid.year, valid.month, "%02i%02i" % (valid.month, valid.day)))


def main():
    if len(sys.argv) == 4:
        do_day(datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                                 int(sys.argv[3])))
    elif len(sys.argv) == 3:
        sts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), 1)
        ets = sts + datetime.timedelta(days=35)
        ets = ets.replace(day=1)
        now = sts
        while now < ets:
            do_day(now)
            now += datetime.timedelta(days=1)
    else:
        do_day(datetime.datetime.now())

if __name__ == '__main__':
    main()
    ccursor.close()
    COOP.commit()
