"""
    Dumping altimeter data so that GEMPAK can analyze it
"""
import datetime
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    ts = datetime.datetime.utcnow().strftime("%y%m%d/%H00")
    pgconn = get_dbconn('iem')
    cursor = pgconn.cursor()

    cursor.execute("""
     SELECT t.id, alti from current c JOIN stations t on (t.iemid = c.iemid)
     WHERE alti > 0 and valid > (now() - '60 minutes'::interval)
     and t.state in ('IA','MO','IL','WI','IN','OH','KY','MI','SD','ND','NE',
     'KS')
     """)

    fh = open('/mesonet/data/iemplot/altm.txt', 'w')
    fh.write((" PARM = ALTM\n\n"
             "    STN    YYMMDD/HHMM      ALTM\n"))

    for row in cursor:
        fh.write("   %4s    %s  %8.2f\n" % (row[0], ts, row[1] * 33.8637526))
    fh.close()


if __name__ == '__main__':
    main()
