"""Convert the raw table data into something faster for website to use"""
import psycopg2
import datetime
import pytz
import sys
import pandas as pd
from pyiem.datatypes import speed
from pandas.io.sql import read_sql

pgconn = psycopg2.connect(database='hads', host='iemdb-hads')


def v(val):
    if pd.isnull(val):
        return None
    return val


def do(ts):
    """ Do a UTC date's worth of data"""
    table = ts.strftime("raw%Y_%m")
    sts = datetime.datetime(ts.year, ts.month, ts.day).replace(tzinfo=pytz.utc)
    ets = sts + datetime.timedelta(hours=24)
    df = read_sql("""
        SELECT station, valid, substr(key, 1, 3) as vname, value
        from """ + table + """
        WHERE valid >= %s and valid < %s and
        substr(key, 1, 3) in ('USI', 'UDI', 'TAI', 'TDI')
        and value > -999
    """, pgconn, params=(sts, ets), index_col=None)

    pdf = pd.pivot_table(df, values='value', index=['station', 'valid'],
                         columns='vname')
    pdf['sknt'] = speed(pdf['USI'].values, 'MPH').value('KT')

    table = ts.strftime("t%Y")
    cursor = pgconn.cursor()
    cursor.execute("""DELETE from """ + table + """ WHERE valid between %s
    and %s""", (sts, ets))
    for (station, valid), row in pdf.iterrows():
        cursor.execute("""INSERT into """ + table + """
        (station, valid, tmpf, dwpf, drct, sknt)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (station, valid, v(row['TAI']), v(row['TDI']), v(row['UDI']),
              v(row['sknt'])))
    cursor.close()
    pgconn.commit()


def main(argv):
    ts = datetime.date.today() - datetime.timedelta(days=1)
    if len(argv) == 4:
        ts = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    do(ts)

if __name__ == '__main__':
    main(sys.argv)
