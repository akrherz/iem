# Dump Altimeter please to a GEMPAK file
import mx.DateTime
ts = mx.DateTime.gmt().strftime("%y%m%d/%H00")
import iemdb
IEM = iemdb.connect("iem", bypass=True)
icursor = IEM.cursor()

icursor.execute("""
 SELECT station, alti from current WHERE alti > 0 
 and valid > (now() - '60 minutes'::interval)
 """)

o = open('alti.txt', 'w')
o.write(""" PARM = ALTI                                                                     

    STN    YYMMDD/HHMM      ALTI
""")

for row in icursor:
  o.write("   %4s    %s  %8.2f\n" % (row[0], ts, row[1]))

o.close()
