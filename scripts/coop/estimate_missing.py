"""
 Crude data estimator!
"""
import sys
import iemdb
import numpy
import network
import psycopg2.extras

# Database Connection
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
ccursor2 = COOP.cursor()

state = sys.argv[1]
nt = network.Table("%sCLIMATE" % (state.upper(),))

# We'll care about our nearest 11 stations, arbitrary
friends = {}
weights = {}
for station in nt.sts.keys():
    sql = """select id, distance(geom, 'SRID=4326;POINT(%s %s)') from stations
         WHERE network = '%sCLIMATE' and id != '%s' 
         and archive_begin < '1951-01-01' and
         substr(id, 3, 1) != 'C' and substr(id, 3,4) != '0000'
         ORDER by distance
         ASC LIMIT 11""" % (nt.sts[station]['lon'], nt.sts[station]['lat'], 
                            state.upper(), station)
    ccursor.execute( sql )
    friends[station] = []
    weights[station] = []
    for row in ccursor:
        friends[station].append( row[0] )
        weights[station].append( 1.0 / row[1] )
    weights[station] = numpy.array( weights[station] )

def do_var(varname):
    """
    Run our estimator for a given variable
    """
    sql = """select day, station from alldata_%s WHERE %s IS NULL 
        and day >= '1893-01-01'""" % (state.lower(), varname)
    ccursor.execute( sql )
    for row in ccursor:
        day = row[0]
        station = row[1]
        if not nt.sts.has_key(station):
            continue

        sql = """SELECT station, %s from alldata_%s WHERE %s is not NULL
            and station in %s and day = '%s'""" % (varname, state, varname,
                                    tuple(friends[station]), day)
        ccursor2.execute(sql)
        weight = []
        value = []
        for row2 in ccursor2:
            idx = friends[station].index(row2[0])
            weight.append( weights[station][idx] )
            value.append( row2[1] )

        if len(weight) < 3:
            print 'Not Enough Data Found station: %s day: %s var: %s' % (
                                    station, day, varname)
            continue
    
        mass = sum(weight)
        interp = numpy.sum(numpy.array(weight) * numpy.array(value) / mass)

        format = '%.2f'
        if varname in ['high', 'low']:
            format = '%.0f'
        print 'Set station: %s day: %s varname: %s value: %s' % (station,
                                    day, varname, format % (interp,))
        sql = """UPDATE alldata_%s SET estimated = true, %s = %s WHERE 
            station = '%s' and day = '%s'""" % (state.lower(), varname, 
                                                interp, station, day)
        ccursor2.execute( sql )

def main():
    for varname in ['high', 'low', 'precip']:
        do_var(varname)    

    ccursor2.close()
    COOP.commit()
    
if __name__ == '__main__':
    main()