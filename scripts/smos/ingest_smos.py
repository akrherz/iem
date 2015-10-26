"""Ingest SMOS data, please!"""

import glob
import os
import psycopg2
import datetime
SMOS = psycopg2.connect(database='smos', host='iemdb')
scursor = SMOS.cursor()


def consume(fp, ts):
    """
    Actually process a file noted at fp and for time ts
    """
    tablets = ts + datetime.timedelta(hours=6)
    table = "data_%s" % (tablets.strftime("%Y_%m"),)
    for line in open(fp):
        tokens = line.replace("\x00", "").strip().split()
        if len(tokens) != 3:
            continue
        (sid, sm, od) = tokens
        sm = float(sm)
        if sm <= 0 or sm >= 0.7:
            sm = None
        od = float(od)
        if od <= 0 or od > 1:
            od = None
        scursor.execute("""
        INSERT into """+table+"""(grid_idx, valid, soil_moisture,
        optical_depth) VALUES (%s, '%s-06', %s, %s)
        """ % (sid,
               ts.strftime("%Y-%m-%d %H:%M"), sm or 'Null',
               od or 'Null'))


def lookforfiles():
    """
    Try to find files to ingest, please
    """
    os.chdir("/mesonet/data/smos")
    files = glob.glob("*.txt")
    for fn in files:
        ts = datetime.datetime.strptime(fn, '%Y_%m_%d_%H%M.txt')
        scursor.execute("""
            SELECT * from obtimes where valid = '%s-06'
        """ % (ts.strftime("%Y-%m-%d %H:%M"),))
        row = scursor.fetchone()
        if row is None:
            # print "INGEST FILE!", file
            consume(fn, ts)
            scursor.execute("""
            INSERT into obtimes(valid) values ('%s-06')
            """ % (ts.strftime("%Y-%m-%d %H:%M"),))
            SMOS.commit()

if __name__ == "__main__":
    lookforfiles()
