"""Process the decagon data"""
import psycopg2
import sys
import datetime
import pandas as pd
import numpy as np

CENTRAL_TIME = ['ISUAG', 'GILMORE', 'SERF']


def translate(df):
    """Translate data columns"""
    x = {}
    for colname in df.columns:
        tokens = colname.split()
        name = None
        if colname.startswith('Port '):
            name = 'd%s' % (tokens[1], )
            if colname.find('Bulk EC') > 0:
                name += "ec"
            elif colname.find('VWC') > 0:
                name += 'moisture'
            else:
                name += "temp"

        if name is not None:
            x[colname] = name

    df.rename(columns=x, inplace=True)


def process1(fn, timefmt='%d-%b-%Y %H:%M:%S'):
    df = pd.read_table(fn, sep='\t', index_col=False)
    df['valid'] = df['Measurement Time'].apply(
        lambda s: datetime.datetime.strptime(s.strip(), timefmt))
    df.drop('Measurement Time', axis=1, inplace=True)
    translate(df)
    return df


def database_save(uniqueid, plot, df):
    pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb')
    cursor = pgconn.cursor()
    minvalid = df['valid'].min()
    maxvalid = df['valid'].max()
    tzoff = "05" if uniqueid not in CENTRAL_TIME else "06"
    cursor.execute("""
        DELETE from decagon_data WHERE
        uniqueid = %s and plotid = %s and valid >= %s and valid < %s
    """, (uniqueid, plot, minvalid.strftime("%Y-%m-%d %H:%M-"+tzoff),
          maxvalid.strftime("%Y-%m-%d %H:%M-"+tzoff)))
    if cursor.rowcount > 0:
        print("DELETED %s rows previously saved!" % (cursor.rowcount, ))

    def v(val):
        if isinstance(val, str):
            if val.strip().lower() in ['nan', ]:
                return 'null'
            return val
        if np.isnan(val):
            return 'null'
        return val
    for _, row in df.iterrows():
        cursor.execute("""
        INSERT into decagon_data(uniqueid, plotid, valid, d1moisture, d1temp,
        d1ec, d2moisture, d2temp, d3moisture, d3temp, d4moisture, d4temp,
        d5moisture, d5temp) VALUES ('%s', '%s', '%s', %s, %s,
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s)
        """ % (uniqueid, plot, row['valid'].strftime("%Y-%m-%d %H:%M-"+tzoff),
               v(row['d1moisture']), v(row['d1temp']), v(row['d1ec']),
               v(row['d2moisture']), v(row['d2temp']),
               v(row['d3moisture']), v(row['d3temp']),
               v(row['d4moisture']), v(row['d4temp']),
               v(row['d5moisture']), v(row['d5temp'])))

    cursor.close()
    pgconn.commit()
    pgconn.close()


def main(argv):
    """Process a file into the database, please!"""
    fmt = argv[1]
    fn = argv[2]
    uniqueid = argv[3]
    plot = argv[4]
    if fmt == '1':
        df = process1(fn)
    elif fmt == '2':
        df = process1(fn, '%m/%d/%y %H:%M %p')
    print(("File: %s found: %s lines for columns %s"
           ) % (fn, len(df.index), df.columns))
    database_save(uniqueid, plot, df)

if __name__ == '__main__':
    main(sys.argv)
