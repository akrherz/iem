#!/usr/bin/env python
import cgi
import datetime
import sys
import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()


def get_data(network, sts, ets, stations=[]):
    ''' Go fetch data please '''
    s = ("station,network,valid,precip_in\n")
    if len(stations) == 1:
        stations.append('ZZZZZ')
    cursor.execute("""SELECT station, network, valid, phour from
        hourly WHERE
        valid >= %s and valid < %s and network = %s and station in %s
        ORDER by valid ASC
        """, (sts, ets, network, tuple(stations)))
    for row in cursor:
        s += "%s,%s,%s,%s\n" % (row[0], row[1], row[2], row[3])

    return s


def main():
    """ run rabbit run """
    sys.stdout.write('Content-type: text/plain\n\n')
    form = cgi.FieldStorage()
    try:
        sts = datetime.date(int(form.getfirst('year1')),
                            int(form.getfirst('month1')),
                            int(form.getfirst('day1')))
        ets = datetime.date(int(form.getfirst('year2')),
                            int(form.getfirst('month2')),
                            int(form.getfirst('day2')))
    except:
        sys.stdout.write(("ERROR: Invalid date provided, please check "
                          "selected dates."))
        return
    stations = form.getlist('station')
    network = form.getfirst('network')[:12]
    sys.stdout.write(get_data(network, sts, ets, stations=stations))

if __name__ == '__main__':
    # Go Main Go
    main()
