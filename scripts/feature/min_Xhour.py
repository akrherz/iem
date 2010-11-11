# Generate some comparison data between ASOS sites, tricky, me thinks

import iemdb
import datetime
import numpy
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
acursor.execute("SET TIME ZONE 'GMT'")

maxv = 0

def get_data(year, station):
    global maxv
    data = {}
    acursor.execute("""SELECT valid, sknt from t"""+year+""" where station = %s
    
    and (extract(minute from valid) between 50 and 59 or 
        extract(minute from valid) = 0)
    and sknt >= 0 ORDER by valid ASC""", (station,
                                    ))
    vals = [0,0,0,0]
    for row in acursor:
        vals.insert(0, row[1] )
        vals.pop()
        if min(vals) >= maxv:
            print vals, min(vals), row[0]
            maxv = min(vals)
        

station1 = 'DSM'
for year in range(1973,2011):
     get_data(str(year), station1)
