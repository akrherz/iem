"""Compute the archive start time of a HADS/DCP network"""
from pyiem.network import Table as NetworkTable
import sys
import psycopg2
import datetime

THISYEAR = datetime.datetime.now().year
HADSDB = psycopg2.connect(database='hads', host='iemdb')
MESOSITEDB = psycopg2.connect(database='mesosite', host='iemdb')


def do(network, sid):
    cursor = HADSDB.cursor()
    for yr in range(2002, THISYEAR + 1):
        cursor.execute("""
            SELECT min(valid) from raw""" + str(yr) + """
            WHERE station = %s
        """, (sid,))
        minv = cursor.fetchone()[0]
        if minv is not None:
            return minv


def do_network(network):
    nt = NetworkTable(network)
    for sid in nt.sts.keys():
        sts = do(network, sid)
        if sts is None:
            continue
        if (nt.sts[sid]['archive_begin'] is None or
                nt.sts[sid]['archive_begin'] != sts):
            osts = nt.sts[sid]['archive_begin']
            f = "%Y-%m-%d %H:%M"
            print(("%s [%s] new sts: %s OLD sts: %s"
                   ) % (sid, network, sts.strftime(f),
                        osts.strftime(f) if osts is not None else 'null'))
            cursor = MESOSITEDB.cursor()
            cursor.execute("""UPDATE stations SET archive_begin = %s
            WHERE id = %s and network = %s""", (sts, sid, network))
            cursor.close()
            MESOSITEDB.commit()


def main(argv):
    """Go main Go"""
    if len(argv) == 1:
        # If we run without args, we pick a "random" network!
        cursor = MESOSITEDB.cursor()
        cursor.execute("""
            SELECT id from networks where id ~* 'DCP'
            ORDER by id ASC
        """)
        networks = []
        for row in cursor:
            networks.append(row[0])
        network = networks[365 % len(networks)]
        print("dbutil/compute_hads_sts.py auto-picked %s" % (network, ))
    else:
        network = argv[1]
    do_network(network)

if __name__ == '__main__':
    main(sys.argv)
