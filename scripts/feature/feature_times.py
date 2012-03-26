import matplotlib.pyplot as plt
import iemdb
import numpy
MESOSITE = iemdb.connect("mesosite", bypass=True)
mcursor = MESOSITE.cursor()

mcursor.execute("""
    SELECT valid from feature ORDER by valid
""")
dates = []
time_of_day = []
for row in mcursor:
    dates.append(row[0])
    time_of_day.append( row[0].hour * 60 + row[0].minute )
    
fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(dates, time_of_day)
ax.set_ylim(0, 24*60)
ax.set_yticks( numpy.arange(0,8) * 180 )
ax.set_yticklabels( ['Mid', '3 AM', '6 AM', '9 AM', 'Noon', '3 PM', '6 PM', '9 PM'])
ax.set_title("IEM Daily Feature Post Time\n2,500 Features since %s" % (dates[0].strftime("%-d %B %Y")))
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')