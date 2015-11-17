"""Dump NASS Quickstats to the IEM database"""
import subprocess
import datetime
import os
import pandas as pd
import psycopg2
import sys

PGCONN = psycopg2.connect(database='coop', host='iemdb')


def get_file():
    """Download and gunzip the file from the FTP site"""
    if os.path.isfile("/mesonet/tmp/qstats.txt"):
        print('    skipping download as we already have the file')
        return
    today = datetime.date.today()
    cmd = ("wget -q -O /mesonet/tmp/qstats.txt.gz "
           "ftp://ftp.nass.usda.gov/quickstats/qs.all_%s.txt.gz"
           ) % (today.strftime("%Y%m%d"), )

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    _ = proc.stdout.read()

    cmd = "cd /mesonet/tmp; gunzip qstats.txt.gz"
    subprocess.Popen(cmd, shell=True)


def database(df):
    """Save df to the database!"""
    cursor = PGCONN.cursor()
    cursor.execute("""SET TIME ZONE 'UTC'""")
    df.columns = [x.lower() for x in df.columns]
    df = df.where((pd.notnull(df)), None)
    df2 = df[df['commodity_desc'].isin(['CORN', 'SOYBEANS'])]
    for _, row in df2.iterrows():
        try:
            value = float(row['value'].replace(",", ""))
        except:
            value = None
        try:
            # If we are not in addall mode, we have to be careful!
            cursor.execute("""INSERT into nass_quickstats(source_desc, sector_desc,
    group_desc,
    commodity_desc,
    class_desc,
    prodn_practice_desc,
    util_practice_desc,
    statisticcat_desc,
    unit_desc,
    agg_level_desc,
    state_alpha,
    asd_code,
    county_ansi,
    zip_5,
    watershed_code,
    country_code,
    year,
    freq_desc,
    begin_code,
    end_code,
    week_ending,
    load_time,
    value,
    cv,
    num_value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (row['source_desc'], row['sector_desc'], row['group_desc'],
                  row['commodity_desc'],
                  row['class_desc'],
                  row['prodn_practice_desc'],
                  row['util_practice_desc'],
                  row['statisticcat_desc'],
                  row['unit_desc'],
                  row['agg_level_desc'],
                  row['state_alpha'],
                  row['asd_code'],
                  row['county_ansi'],
                  row['zip_5'],
                  row['watershed_code'],
                  row['country_code'],
                  row['year'],
                  row['freq_desc'],
                  row['begin_code'],
                  row['end_code'],
                  row['week_ending'],
                  row['load_time'],
                  row['value'],
                  row['cv_%'],
                  value))
        except Exception, exp:
            print exp
            for key in row.keys():
                print key, row[key], len(str(row[key]))
            sys.exit()
    print('    processed %6s lines from %6s candidates' % (len(df2.index),
                                                           len(df.index)))
    cursor.close()
    PGCONN.commit()


def process():
    """Do some work"""
    # The file is way too big (11+ GB) to be reliably read into pandas, so
    # we need to do some chunked processing.
    cursor = PGCONN.cursor()
    cursor.execute("""
            truncate nass_quickstats
    """)
    cursor.close()
    PGCONN.commit()
    header = ""
    tmpfn = None
    accumlines = 0
    for linenum, line in enumerate(open("/mesonet/tmp/qstats.txt")):
        if linenum == 0:
            header = line
        if tmpfn is None:
            tmpfn = '/mesonet/tmp/tempor.txt'
            o = open(tmpfn, 'w')
            o.write(header+"\n")
        if linenum > 0:
            o.write(line+"\n")
            accumlines += 1
        if accumlines >= 600000:
            o.close()
            df = pd.read_csv(tmpfn, sep='\t', low_memory=False)
            database(df)
            tmpfn = None
            accumlines = 0
    if accumlines > 0:
        o.close()
        df = pd.read_csv(tmpfn, sep='\t', low_memory=False)
        database(df)


def cleanup():
    for fn in ['/mesonet/tmp/qstats.txt', '/mesonet/tmp/tempor.txt']:
        print('    Deleted %s' % (fn, ))
        os.unlink(fn)

if __name__ == '__main__':
    print("scripts/ingestors/nass_quickstats.py")
    get_file()
    process()
    if len(sys.argv) == 1:
        cleanup()
    print("done...")
