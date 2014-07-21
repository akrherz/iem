"""
    Dumping altimeter data so that GEMPAK can analyze it
"""
import datetime
import psycopg2

ts = datetime.datetime.utcnow().strftime("%y%m%d/%H00")
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

cursor.execute("""
 SELECT t.id, alti from current c JOIN stations t on (t.iemid = c.iemid)
 WHERE alti > 0 and valid > (now() - '60 minutes'::interval)
 and t.state in ('IA','MO','IL','WI','IN','OH','KY','MI','SD','ND','NE','KS')
 """)

o = open('/mesonet/data/iemplot/altm.txt', 'w')
o.write(""" PARM = ALTM                                                                     

    STN    YYMMDD/HHMM      ALTM
""")

for row in cursor:
    o.write("   %4s    %s  %8.2f\n" % (row[0], ts, row[1] * 33.8637526))

o.close()
