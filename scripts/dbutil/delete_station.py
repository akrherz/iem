"""Delete a station and all references to it!"""
import psycopg2
import sys


def main():
    if len(sys.argv) != 3:
        print 'Usage: python remove_realtime.py NETWORK SID'
        sys.exit()
    network = sys.argv[1]
    station = sys.argv[2]
    IEM = psycopg2.connect(database='iem', host='iemdb')
    icursor = IEM.cursor()
    MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
    mcursor = MESOSITE.cursor()
    delete_logic(icursor, mcursor, network, station)
    icursor.close()
    IEM.commit()
    mcursor.close()
    MESOSITE.commit()


def delete_logic(icursor, mcursor, network, station):
    for table in ['current', 'summary']:
        icursor.execute("""
         DELETE from %s where
         iemid = (select iemid from stations
                  where id = '%s' and network = '%s')
        """ % (table, station, network))
        print(('Updating table: %s resulted in %s rows removed'
               ) % (table, icursor.rowcount))

    mcursor.execute("""
        DELETE from stations where id = '%s' and network = '%s'
    """ % (station, network))
    print(('Updating mesosite resulted in %s rows removed'
           ) % (mcursor.rowcount, ))


if __name__ == '__main__':
    main()
