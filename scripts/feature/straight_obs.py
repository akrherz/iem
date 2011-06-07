import iemdb
import math
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""
 select to_char(valid, 'YYMMDDHH24') from alldata where station = 'FSD' and metar ~* 'SN' ORDER by valid ASC
""")

obs = {}
for row in acursor:
    obs[ row[0] ] = 1
    
import mx.DateTime

sts = mx.DateTime.DateTime(1940,1,1)
ets = mx.DateTime.DateTime(2011,1,12)
interval = mx.DateTime.RelativeDateTime(hours=1)

now = sts
mrun = 1
while now < ets:
    running = 0
    while obs.has_key( now.strftime("%y%m%d%H")):
        running += 1
        now += interval
    if running >= mrun:
        print running, now
        mrun = running
    if running > 49:
        print running, now
    now += interval