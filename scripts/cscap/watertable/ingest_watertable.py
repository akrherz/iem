import pandas as pd
import psycopg2
import sys
import datetime
import numpy as np

CENTRAL_TIME = ['ISUAG', 'GILMORE', 'SERF']


def process3(fn):
    """ Format 3, STJOHNS"""
    df = pd.read_excel(fn, sheetname=None)
    for plotid in df:
        print plotid, df[plotid].columns
        df[plotid].dropna(inplace=True)
        df[plotid]['valid'] = df[plotid][['Date', 'Time']].apply(
            lambda x: datetime.datetime.strptime("%s/%s/%s %s" % (x[0].month,
                                                            x[0].day,
                                                            x[0].year, x[1]),
                                                 '%m/%d/%Y %H:%M:%S'),
                                                                 axis=1)
        df[plotid]['depth'] = df[plotid]['Water Table Depth below Ground'] * 10.
    return df


def process2(fn):
    """ Format 2, SERF"""
    df = pd.read_excel(fn, sheetname=None, skiprows=[0, ], parse_cols="H,I")
    for plotid in df:
        print plotid, df[plotid].columns
        df[plotid].dropna(inplace=True)
        df[plotid]['valid'] = df[plotid]['Date-Time']
        df[plotid]['depth'] = df[plotid]['Level below ground'] * 0.3048 * 1000.
    return df


def process1(fn):
    """Format 1, DPAC"""
    df = pd.read_csv(fn, sep='\t')
    df.columns = ['valid', 'depth']
    df['depth'] = pd.to_numeric(df['depth'], errors='coerce')
    df['depth'] = df['depth'] * 1000.
    df['valid'] = df['valid'].apply(
        lambda s: datetime.datetime.strptime(s.strip(), '%m/%d/%Y %H:%M'))
    df.dropna(inplace=True)
    return df


def database_save(df, uniqueid, plotid):
    pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb')
    cursor = pgconn.cursor()
    for i, row in df.iterrows():
        if not isinstance(row['valid'], datetime.datetime):
            print('Row df.index=%s, valid=%s, culling' % (i, row['valid']))
            df.drop(i, inplace=True)
    minvalid = df['valid'].min()
    maxvalid = df['valid'].max()
    print("Time Domain: %s - %s" % (minvalid, maxvalid))

    # Data is always standard time, this is why this works
    tzoff = "05" if uniqueid not in CENTRAL_TIME else "06"
    cursor.execute("""
        DELETE from watertable_data WHERE
        uniqueid = %s and plotid = %s and valid >= %s and valid <= %s
    """, (uniqueid, plotid, minvalid.strftime("%Y-%m-%d %H:%M-"+tzoff),
          maxvalid.strftime("%Y-%m-%d %H:%M-"+tzoff)))

    if cursor.rowcount > 0:
        print("DELETED %s rows previously saved!" % (cursor.rowcount, ))

    def v(row, name):
        val = row.get(name)
        if val is None:
            return 'null'
        if isinstance(val, str):
            if val.strip().lower() in ['nan', ]:
                return 'null'
            return val
        # elif isinstance(val, pd.core.series.Series):
        #    print val
        #    print row
        #    sys.exit()
        try:
            if np.isnan(val):
                return 'null'
        except Exception, exp:
            print exp
            print(('Plot: %s Val: %s[%s] Name: %s Valid: %s'
                   ) % (plotid, val, type(val), name, row['valid']))
            return 'null'
        return val
    for _, row in df.iterrows():
        cursor.execute("""
        INSERT into watertable_data(uniqueid, plotid, valid,
        depth_mm, depth_mm_qc) VALUES ('%s', '%s', '%s', %s, %s)
        """ % (uniqueid, plotid,
               row['valid'].strftime("%Y-%m-%d %H:%M-"+tzoff),
               v(row, 'depth'), v(row, 'depth')))

    print("Processed %s entries" % (len(df.index), ))
    cursor.close()
    pgconn.commit()
    pgconn.close()


def main(argv):
    fn = argv[1]
    fmt = argv[2]
    uniqueid = argv[3]
    plotid = argv[4]
    if fmt == '1':
        df = process1(fn)
        database_save(df, uniqueid, plotid)
    elif fmt == '2':
        df = process2(fn)
        for plotid in df:
            database_save(df[plotid], uniqueid, plotid)
    elif fmt == '3':
        df = process3(fn)
        for plotid in df:
            database_save(df[plotid], uniqueid, plotid)


if __name__ == '__main__':
    main(sys.argv)
