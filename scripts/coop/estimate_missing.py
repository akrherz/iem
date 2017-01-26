"""Crude estimator of IEM Climate Stations

This is only run for the exceptions, when data is marked as missing for some
reason.  The main data estimator is found at `../climodat/daily_estimator.py`.

This script utilizes the IEMRE web service to provide data.
"""
import sys
from pyiem.network import Table as NetworkTable
import requests
import psycopg2

# Database Connection
COOP = psycopg2.connect(database='coop', host='iemdb')
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

state = sys.argv[1]
nt = NetworkTable("%sCLIMATE" % (state.upper(),))

URI = ("http://iem.local/iemre/daily/"
       "%(date)s/%(lat)s/%(lon)s/json")


def do_var(varname):
    """Run our estimator for a given variable"""
    sql = """
        select day, station from alldata_%s WHERE %s is null
        and day >= '1893-01-01' ORDER by day ASC
        """ % (state.lower(), varname)
    ccursor.execute(sql)
    dataformat = '%.0f' if varname in ['high', 'low'] else '%.2f'

    for row in ccursor:
        day = row[0]
        station = row[1]
        if station not in nt.sts:
            continue
        temp24hour = nt.sts[station]['temp24_hour']
        prefix = "12z_" if temp24hour != 0 else 'daily_'
        units = '_in' if varname == 'precip' else '_f'

        wsuri = URI % {'date': day.strftime("%Y-%m-%d"),
                       'lon': nt.sts[station]['lon'],
                       'lat': nt.sts[station]['lat']}
        req = requests.get(wsuri)
        try:
            estimated = req.json()['data'][0]
        except:
            print("\n%s Failure:%s\n%s" % (station, req.content, wsuri))
            continue
        newvalue = estimated["%s%s%s" % (prefix, varname, units)]

        print(('Set station: %s day: %s varname: %s value: %s'
               ) % (station, day, varname, dataformat % (newvalue,)))
        sql = """
            UPDATE alldata_%s SET estimated = true, %s = %s WHERE
            station = '%s' and day = '%s'
            """ % (state.lower(), varname,
                   dataformat % (newvalue,), station, day)
        sql = sql.replace(' nan ', ' null ')
        ccursor2.execute(sql)


def main():
    for varname in ['high', 'low', 'precip']:
        do_var(varname)

    ccursor2.close()
    COOP.commit()

if __name__ == '__main__':
    main()
