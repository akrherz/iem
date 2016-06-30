"""
 Crude data estimator!
"""
import sys
import numpy as np
from pyiem.network import Table as NetworkTable
import psycopg2.extras
import netCDF4
import datetime
from pyiem import iemre
from pyiem.datatypes import temperature, distance

# Database Connection
COOP = psycopg2.connect(database='coop', host='iemdb')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
ccursor2 = COOP.cursor()

state = sys.argv[1]
nt = NetworkTable("%sCLIMATE" % (state.upper(),))

vnameconv = {'high': 'high_tmpk', 'low': 'low_tmpk', 'precip': 'p01d'}

# We'll care about our nearest 11 stations, arbitrary
friends = {}
weights = {}
for station in nt.sts.keys():
    sql = """
        select id, ST_distance(geom, 'SRID=4326;POINT(%s %s)') from stations
         WHERE network = '%sCLIMATE' and id != '%s'
         and archive_begin < '1951-01-01' and
         substr(id, 3, 1) != 'C' and substr(id, 3,4) != '0000'
         ORDER by st_distance
         ASC LIMIT 11""" % (nt.sts[station]['lon'], nt.sts[station]['lat'],
                            state.upper(), station)
    ccursor.execute(sql)
    friends[station] = []
    weights[station] = []
    for row in ccursor:
        friends[station].append(row[0])
        weights[station].append(1.0 / row[1])
    weights[station] = np.array(weights[station])


def do_var(varname):
    """
    Run our estimator for a given variable
    """
    currentnc = None
    sql = """select day, station from alldata_%s WHERE %s is null
        and day >= '1893-01-01' ORDER by day ASC""" % (state.lower(), varname)
    ccursor.execute(sql)
    for row in ccursor:
        day = row[0]
        station = row[1]
        if station not in nt.sts:
            continue

        sql = """
            SELECT station, %s from alldata_%s WHERE %s is not NULL
            and station in %s and day = '%s'
            """ % (varname, state, varname, tuple(friends[station]), day)
        ccursor2.execute(sql)
        weight = []
        value = []
        for row2 in ccursor2:
            idx = friends[station].index(row2[0])
            weight.append(weights[station][idx])
            value.append(row2[1])

        if len(weight) < 3:
            # Nearest neighbors failed, so lets look at our grided analysis
            # and sample from it
            if currentnc is None or currentnc.title.find(str(day.year)) == -1:
                currentnc = netCDF4.Dataset(("/mesonet/data/iemre/"
                                             "%s_mw_daily.nc") % (day.year,))
            tidx = iemre.daily_offset(datetime.datetime(day.year, day.month,
                                                        day.day))
            iidx, jidx = iemre.find_ij(nt.sts[station]['lon'],
                                       nt.sts[station]['lat'])
            iemreval = currentnc.variables[vnameconv[varname]][tidx, jidx,
                                                               iidx]
            if varname in ('high', 'low'):
                interp = temperature(iemreval, 'K').value('F')
            else:
                interp = distance(iemreval, 'MM').value('IN')
            print '--> Neighbor failure, %s %s %s' % (station, day, varname)
        else:
            mass = sum(weight)
            interp = np.sum(np.array(weight) * np.array(value) / mass)

        dataformat = '%.2f'
        if varname in ['high', 'low']:
            dataformat = '%.0f'
        print(('Set station: %s day: %s varname: %s value: %s'
               ) % (station, day, varname, dataformat % (interp,)))
        sql = """
            UPDATE alldata_%s SET estimated = true, %s = %s WHERE
            station = '%s' and day = '%s'
            """ % (state.lower(), varname,
                   dataformat % (interp,), station, day)
        sql = sql.replace(' nan ', ' null ')
        ccursor2.execute(sql)


def main():
    for varname in ['high', 'low', 'precip']:
        do_var(varname)

    ccursor2.close()
    COOP.commit()

if __name__ == '__main__':
    main()
