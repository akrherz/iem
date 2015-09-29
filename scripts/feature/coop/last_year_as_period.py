import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import datetime

def do():
    sts = datetime.datetime(2013,4,2)
    years = []
    for i in range(1,60):
        ets = sts - datetime.timedelta(days=i)
        ccursor.execute("""SELECT year, avg((high+low)/2.) from alldata_ia
        WHERE station = 'IA0200' and sday < '0403' and sday >= '%s'
        GROUP by year ORDER by year DESC""" % (ets.strftime("%m%d"),))
        for j, row in enumerate(ccursor):
            if j == 0:
                thisyear = row[1]
                continue
            if row[1] <= thisyear:
                print i, thisyear, row[0], row[1]
                years.append( float(row[0]) )
                break
    return years

years = do()
#years = [1993.0, 1993.0, 2008.0, 2008.0, 2011.0, 2011.0, 2011.0, 2011.0, 2011.0, 2011.0, 2001.0, 1983.0, 1983.0, 1983.0, 1983.0, 1983.0, 1983.0, 1983.0, 1984.0, 1993.0, 1993.0, 1993.0, 1993.0, 1993.0, 1993.0, 1993.0, 1984.0, 1984.0, 1984.0, 1984.0, 1984.0, 1984.0, 1984.0, 1975.0, 1993.0, 1993.0, 1993.0, 1993.0, 1993.0, 1993.0, 1993.0, 1993.0, 1993.0, 1993.0, 2001.0, 2001.0, 2001.0, 2001.0, 2001.0, 2001.0, 2008.0, 2008.0, 2008.0, 2008.0, 2008.0, 2008.0, 2008.0, 2008.0, 2008.0]
print years

import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import numpy

years = numpy.array( years )

(fig, ax) = plt.subplots(1,1)

bars = ax.bar( numpy.arange(1,60)-0.4, 2013.0 - years)
last = None
for i, yr in enumerate(years):
    if yr != last:
        x = i
        if i == 0:
            x = -2.5
        text = ax.text( x+1, 2013 - yr + 0.5, "%.0f"  % (yr,), ha='left', va='bottom')
        text.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="yellow")])

    last = yr
ax.set_yticks( range(3,63,10) )
ax.set_yticklabels( range(2010,1940,-10) )
ax.set_title("2013 Ames Average Temperature Coldest Period Since")
ax.set_xlabel("Period of Days prior to 2 April")
ax.set_ylabel("Previous Year Colder than 2013")

ax.grid(True)

fig.savefig('test.png')
