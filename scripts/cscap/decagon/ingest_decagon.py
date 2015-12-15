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
    # print df.columns
    for colname in df.columns:
        tokens = colname.split()
        name = None
        if colname.find('Measurement Time') > 0:
            name = "valid"
        elif colname.startswith('Port '):
            name = 'd%s' % (tokens[1].split(".")[0], )
            if colname.find('Bulk EC') > 0:
                name += "ec"
            elif colname.find('VWC') > 0:
                name += 'moisture'
            else:
                name += "temp"

        if name is not None:
            x[colname] = name

    df.rename(columns=x, inplace=True)


def process1(fn, timefmt='%m/%d/%y %H:%M'):
    df = pd.read_table(fn, sep='\t', index_col=False)
    df['valid'] = df['Measurement Time'].apply(
        lambda s: datetime.datetime.strptime(s.strip(), timefmt))
    df.drop('Measurement Time', axis=1, inplace=True)
    translate(df)
    return df


def process4(fn):
    """See MASON for an example"""
    df = pd.read_excel(fn, index_col=False, skiprows=[0, 1, 3, 4, 5])
    x = {'20': 'd2', '40': 'd3', '60': 'd4', '80': 'd5'}
    extract = {}
    for col in df.columns[1:]:
        plotid = col[:-3]
        depth = col[-2:]
        e = extract.setdefault(plotid, [df.columns[0]])
        e.append(col)
    print extract
    mydict = {}
    for plotid in extract.keys():
        mydict[plotid] = df[extract[plotid]].copy()
        rename = {df.columns[0]: 'valid'}
        for col in mydict[plotid].columns[1:]:
            depth = col[-2:]
            rename[col] = "%smoisture" % (x[depth], )
        mydict[plotid].rename(columns=rename, inplace=True)
        print mydict[plotid].columns
    return mydict


def process3(fn):
    mydict = pd.read_excel(fn, sheetname=None, index_col=False)
    # Need to load up rows 0 and 1 into the column names
    for sheetname in mydict:
        df = mydict[sheetname]
        row0 = df.iloc[0, :]
        row1 = df.iloc[1, :]
        reg = {df.columns[0]: 'valid'}
        for c, r0, r1 in zip(df.columns, row0, row1):
            reg[c] = "%s %s %s" % (c, r0, r1)
        df.rename(columns=reg, inplace=True)
        df.drop(df.head(2).index, inplace=True)
        translate(df)
    return mydict


def database_save(uniqueid, plot, df):
    pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb')
    cursor = pgconn.cursor()
    for i, val in enumerate(df['valid']):
        if not isinstance(val, datetime.datetime):
            print i, val
    minvalid = df['valid'].min()
    maxvalid = df['valid'].max()
    tzoff = "05" if uniqueid not in CENTRAL_TIME else "06"
    cursor.execute("""
        DELETE from decagon_data WHERE
        uniqueid = %s and plotid = %s and valid >= %s and valid <= %s
    """, (uniqueid, plot, minvalid.strftime("%Y-%m-%d %H:%M-"+tzoff),
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
        try:
            if np.isnan(val):
                return 'null'
        except Exception, exp:
            print exp
            print(('Val: %s[%s] Name: %s Valid: %s'
                   ) % (val, type(val), name, row['valid']))
            return 'null'
        return val
    for _, row in df.iterrows():
        cursor.execute("""
        INSERT into decagon_data(uniqueid, plotid, valid, d1moisture, d1temp,
        d1ec, d2moisture, d2temp, d3moisture, d3temp, d4moisture, d4temp,
        d5moisture, d5temp, d1moisture_qc, d1temp_qc,
        d1ec_qc, d2moisture_qc, d2temp_qc, d3moisture_qc, d3temp_qc,
        d4moisture_qc, d4temp_qc,
        d5moisture_qc, d5temp_qc) VALUES ('%s', '%s', '%s', %s, %s,
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s)
        """ % (uniqueid, plot, row['valid'].strftime("%Y-%m-%d %H:%M-"+tzoff),
               v(row, 'd1moisture'), v(row, 'd1temp'), v(row, 'd1ec'),
               v(row, 'd2moisture'), v(row, 'd2temp'),
               v(row, 'd3moisture'), v(row, 'd3temp'),
               v(row, 'd4moisture'), v(row, 'd4temp'),
               v(row, 'd5moisture'), v(row, 'd5temp'),
               v(row, 'd1moisture'), v(row, 'd1temp'), v(row, 'd1ec'),
               v(row, 'd2moisture'), v(row, 'd2temp'),
               v(row, 'd3moisture'), v(row, 'd3temp'),
               v(row, 'd4moisture'), v(row, 'd4temp'),
               v(row, 'd5moisture'), v(row, 'd5temp')))

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
    elif fmt == '3':
        df = process3(fn)
    elif fmt == '4':
        df = process4(fn)
    if isinstance(df, dict):
        for plot in df:
            print(("File: %s[%s] found: %s lines for columns %s"
                   ) % (fn, plot, len(df[plot].index), df[plot].columns))
            database_save(uniqueid, plot, df[plot])
    else:
        print(("File: %s found: %s lines for columns %s"
               ) % (fn, len(df.index), df.columns))
        database_save(uniqueid, plot, df)

if __name__ == '__main__':
    main(sys.argv)
