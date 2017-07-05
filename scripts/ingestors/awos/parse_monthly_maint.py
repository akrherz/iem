"""
 Parse the monthly maint file I get from the DOT

  id         | integer |
 station    | character varying(10)    |
 portfolio  | character varying(10)    |
 valid      | timestamp with time zone |
 parameter  | character varying(10)    |
 adjustment | real                     |
 final      | real                     |
 comments   | text                     |

"""
from __future__ import print_function
import sys
import re
import datetime

import psycopg2
import pandas as pd

CALINFO = re.compile((r".* AWOS t/d:?\s*([0-9\-\.]+)/([0-9\-\.]+)\s+"
                      r"Std\.?\s*t?/?d?:?\s*([0-9\-\.]+)/([0-9\-\.]+)"),
                     re.IGNORECASE)
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'


def main(argv):
    """Go Main"""
    # Use SSH proxy
    pgconn = psycopg2.connect(dbname="portfolio", host="localhost",
                              port=5555, user="nobody")
    pcursor = pgconn.cursor()

    df = pd.read_csv(argv[1])

    for _, row in df.iterrows():
        date = datetime.datetime.strptime(row['Visit Date'], '%d-%b-%y')

        if row['Description'].startswith('site offline'):
            continue
        parts = re.findall(CALINFO, row['Description'])
        if len(parts) == 0:
            print(FAIL + row['Description'] + ENDC)
            continue
        faa = row['FAA Code']
        sql = """
        INSERT into iem_calibration(station, portfolio, valid, parameter,
        adjustment, final, comments) values (%s, 'iaawos', %s, %s, %s, %s, %s)
        """
        tempadj = float(parts[0][2]) - float(parts[0][0])
        args = (faa, date.strftime("%Y-%m-%d"), 'tmpf', tempadj,
                parts[0][2], row['Description'].replace('"', ''))
        if len(sys.argv) > 1:
            pcursor.execute(sql, args)

        dewpadj = float(parts[0][3]) - float(parts[0][1])
        args = (faa, date.strftime("%Y-%m-%d"), 'dwpf',
                float(parts[0][3]) - float(parts[0][1]),
                parts[0][3], row['Description'].replace('"', ''))
        if len(sys.argv) > 1:
            pcursor.execute(sql, args)

        print(('--> %s [%s] TMPF: %s (%s) DWPF: %s (%s)'
               ) % (faa, date, parts[0][2], tempadj,
                    parts[0][3], dewpadj))

    if len(argv) == 2:
        print('WARNING: Disabled, call with arbitrary argument to enable')
    else:
        pcursor.close()
        pgconn.commit()
        pgconn.close()


if __name__ == '__main__':
    main(sys.argv)
