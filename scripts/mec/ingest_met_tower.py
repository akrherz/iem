"""Pull in the met_tower dataset """
import psycopg2
import glob
import os
import datetime

def make_none(val):
    """Check the value and make sure it is okay """
    if float(val) < -990:
        return None
    return float(val)

def main():
    """Do Something"""
    pgconn = psycopg2.connect(database='mec', host='iemdb')
    cursor = pgconn.cursor()

    os.chdir("/tmp/winddata")
    fns = glob.glob("P*.txt")
    for fn in fns:
        for line in open(fn):
            (mo, dy, yr, hr, mi, w80, d80, t80, p80, 
             w40, d40, t40, p40) = line.strip().split()
            
            ts = datetime.datetime(int(yr), int(mo), int(dy), int(hr),
                                   int(mi))
    
            cursor.execute("""INSERT into met_tower_data(valid, wmps_80,
            drct_80, tmpc_80, pres_80, wmps_40, drct_40, tmpc_40, pres_40)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (
                ts.strftime("%Y-%m-%d %H:%M")+"-06:00",
                make_none(w80), make_none(d80), make_none(t80), make_none(p80),
                make_none(w40), make_none(d40), make_none(t40), make_none(p40)))

    cursor.close()
    pgconn.commit()
    pgconn.close()

if __name__ == '__main__':
    main()