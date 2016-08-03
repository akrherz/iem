#!/usr/bin/env python
"""Provide some CSV Files

first four columns need to be
ID,Station,Latitude,Longitude
"""
import cgi
import sys
import psycopg2
from pandas.io.sql import read_sql

#>> *         Road condition dots
#>> *         DOT plows
#>> *         RWIS sensor data
#>> *         River gauges
#>> *         Ag data (4" soil temps)


def do_webcams(network):
    """direction arrows"""
    pgconn = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
    df = read_sql("""
    select cam as id, w.name as station, st_y(geom) as latitude,
    st_x(geom) as longitude, drct
    from camera_current c JOIN webcams w on (c.cam = w.id)
    WHERE c.valid > (now() - '30 minutes'::interval) and w.network = %s
    """, pgconn, params=(network,))
    return df


def router(q):
    """Process and return dataframe"""
    if q == 'iaroadcond':
        df = do_iaroadcond()
    elif q == 'iadotplows':
        df = do_iadotplows()
    elif q == 'iarwis':
        df = do_iariws()
    elif q == 'iariver':
        df = do_iariver()
    elif q == 'isusm':
        df = do_isusm()
    elif q == 'kcrgcitycam':
        df = do_webcams('KCRG')
    else:
        sys.stdout.write("""ERROR, unknown report specified""")
        sys.exit()
    return df


def main():
    """Do Something"""
    form = cgi.FieldStorage()
    q = form.getfirst('q')
    sys.stdout.write("Content-type: text/plain\n\n")
    df = router(q)
    sys.stdout.write(df.to_csv(None, index=False))

if __name__ == '__main__':
    main()
