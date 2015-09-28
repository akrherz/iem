"""
 We start with TONIGHT
 Then the next day is index 2
"""
from pyiem.nws.product import TextProduct, ugc
import datetime
import numpy
import psycopg2
AFOS = psycopg2.connect(database='afos', host='iemdb', user='nobody')
acursor = AFOS.cursor()

def run(ts, data):
    p = TextProduct( data )
    
    today = p.valid
    indices = ['TONIGHT']
    for i in range(1,8):
        d2 = (today + datetime.timedelta(days=i)).strftime("%A").upper()
        indices.append(d2)
        indices.append(d2 + " NIGHT")
        
    
    def find_index(dstring):
        tokens = dstring.replace(".", "").split("AND")
        i = []
        for token in tokens:
            d2 = token.strip()
            if d2 not in indices:
                #print '%s not in indices' % (d2,)
                i.append( None )
            else:
                i.append( indices.index( d2 ) )
        return i
    
    polk = ugc.UGC("IA", "Z", 60)
    for seg in p.segments:
        if polk not in seg.ugcs:
            continue
        tokens = seg.unixtext.split(".TONIGHT...")
        if len(tokens) != 2:
            continue
        meat = ".TONIGHT..."+tokens[1]
        running = ""
        sections = []
        for line in meat.split("\n"):
            if len(line) > 0 and line[0] == '.': # new
                if running != "":
                    sections.append( running )
                    running = ""
            running += line +" "
            
        ids = []
        for section in sections:
            if section.find(" 0 PERCENT") > 0:
                idexs = find_index( section.split("...",1)[0] )
                for i in idexs:
                    ids.append( i )
        return ids
#"""
acursor.execute("""
 select entered, data from products where pil = 'ZFPDMX'
 and extract(hour from entered) in (15,16)
 ORDER by entered DESC
""")
last = None

zeros = numpy.zeros((13,))
for row in acursor:
    day = row[0].strftime("%Y%m%d")
    if day == last:
        continue
    last = day
    ids = run( row[0], row[1] )
    if ids is None:
        print 'Bad Processing', row[0]
        continue
    for i in ids:
        if i is not None:
            zeros[i] += 1.0
        else:
            print 'Missed event', row[0]
print zeros
#"""
data = numpy.array( [64. , 31.,  27. ,  8. ,  4. ,  2. ,  2. ,  1. ,  0. ,  0. ,  0.  , 0. ,  0.])
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

bars = ax.bar( numpy.arange(13)-0.4, data)
for i in range(8):
    ax.text( i, data[i]+2, "%.0f" % (data[i],), ha='center')
ax.set_xticks(numpy.arange(9))
ax.set_xticklabels(["Tonight", "Tomrw.", "Tomrw.\nNight", "Day\n2", "Day 2\nNight",
                    "Day 3", "Day 3\nNight","Day 4", "Day 4\nNight",])
ax.set_xlim(-0.5, 7.5)
ax.set_title("Des Moines NWS 100% Chance of Precipitation Forecast\nAfternoon ZFP for Polk County 1 Jan 2009 - 18 Feb 2013")
ax.set_ylabel("Events (out of 1145 forecasts)")

fig.savefig('test.png')
