"""Figure out when the ISUSM data started..."""
from __future__ import print_function
import datetime

import psycopg2
from pyiem.network import Table as NetworkTable
import pytz


def main():
    """Go Main"""
    basets = datetime.datetime.now()
    basets = basets.replace(tzinfo=pytz.timezone("America/Chicago"))

    isuag = psycopg2.connect(database='isuag', host='iemdb')
    icursor = isuag.cursor()
    mesosite = psycopg2.connect(database='mesosite', host='iemdb')
    mcursor = mesosite.cursor()

    table = NetworkTable("ISUSM")

    icursor.execute("""SELECT station, min(valid), max(valid) from sm_hourly
                    GROUP by station ORDER by min ASC""")
    for row in icursor:
        station = row[0]
        if station not in table.sts:
            print(('Whoa station: %s does not exist in metadatabase?'
                   ) % (station, ))
            continue
        if table.sts[station]['archive_begin'] != row[1]:
            print(('Updated %s STS WAS: %s NOW: %s'
                   '') % (station, table.sts[station]['archive_begin'],
                          row[1]))

        mcursor.execute("""UPDATE stations SET archive_begin = %s
             WHERE id = %s and network = %s""", (row[1], station, 'ISUSM'))
        if mcursor.rowcount == 0:
            print('ERROR: No rows updated')

    mcursor.close()
    mesosite.commit()
    mesosite.close()


if __name__ == '__main__':
    main()
