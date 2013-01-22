"""
 Check how much HADSA data we have
"""
import os
import sys
import stat
import iemdb
HADS = iemdb.connect('iem', bypass=True)
hcursor = HADS.cursor()

def check():
    hcursor.execute("""SELECT count(*) from current_shef 
    WHERE valid > now() - '1 hour'::interval""")
    row = hcursor.fetchone()

    return row[0]
    
if __name__ == '__main__':
    count = check()
    if count > 10000:
        print 'OK - %s count |count=%s;1000;5000;10000' % (count, count)
        sys.exit(0)
    elif count > 5000:
        print 'WARNING - %s count |count=%s;1000;5000;10000' % (count, count)
        sys.exit(1)
    else:
        print 'CRITICAL - %s count |count=%s;1000;5000;10000' % (count, count)
        sys.exit(2)