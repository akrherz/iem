"""Utility script to compare database counts

    python compare_counts.py <optional_database_name>
"""
from __future__ import print_function
import sys

from pyiem.util import get_dbconn
import tqdm


def main(argv):
    """Go!"""
    oldpg = get_dbconn('postgis', user='mesonet')

    dbs = []
    if len(argv) == 2:
        dbs.append(argv[1])
    else:
        cursor = oldpg.cursor()
        cursor.execute("""
            SELECT datname FROM pg_database
            WHERE datistemplate = false ORDER by datname
        """)
        for row in cursor:
            dbs.append(row[0])

    for db in dbs:
        print("running %s..." % (db,))
        oldpg = get_dbconn(db, user='mesonet')
        ocursor = oldpg.cursor()
        # TODO bug
        newpg = get_dbconn(db, port=5557, user='mesonet')
        ncursor = newpg.cursor()

        tables = []
        ocursor.execute("""
            SELECT table_name
            FROM information_schema.tables WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        for row in ocursor:
            # skip the agg tables as they are just too massive
            if row[0].startswith('alldata'):
                continue
            tables.append(row[0])

        for table in tqdm.tqdm(tables):
            ocursor.execute("""SELECT count(*) from """+table)
            ncursor.execute("""SELECT count(*) from """+table)
            orow = ocursor.fetchone()
            nrow = ncursor.fetchone()
            if orow[0] != nrow[0]:
                print("%s->%s old:%s new:%s" % (db, table, orow[0], nrow[0]))


if __name__ == '__main__':
    main(sys.argv)
