# Dump Altimeter please to a GEMPAK file
import mx.DateTime
ts = mx.DateTime.gmt().strftime("%y%m%d/%H00")
import iemdb
IEM = iemdb.connect("iem", bypass=True)
icursor = IEM.cursor()

icursor.execute("""
 SELECT t.id, alti from current c, stations t WHERE alti > 0 and t.iemid = c.iemid 
 and valid > (now() - '60 minutes'::interval)
 """)

o = open('altm.txt', 'w')
o.write(""" PARM = ALTM                                                                     

    STN    YYMMDD/HHMM      ALTM
""")

for row in icursor:
  o.write("   %4s    %s  %8.2f\n" % (row[0], ts, row[1] * 33.8637526))

o.close()
