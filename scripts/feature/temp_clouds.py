import iemdb, numpy, datetime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

def do(station):
  acursor.execute("""
  select valid, tmpf, skyc1, skyc2, skyc3, skyc4 from t2011 where station = %s and extract(hour from valid) = 5 ORDER by valid ASC
  """, (station,))

  clear = numpy.zeros( (12,), 'f')
  other = numpy.zeros( (12,), 'f')
  overcast = numpy.zeros( (12,), 'f')

  ldate = datetime.datetime(2010,12,31).strftime("%Y%m%d")
  for row in acursor:
    if row[0].strftime("%Y%m%d") == ldate:
      continue
    ldate = row[0].strftime("%Y%m%d")
    month = row[0].month - 1
    if row[2] == 'CLR':
      clear[month] += 1
    elif 'OVC' in row[2:]:
      overcast[month] += 1
    else:
      other[month] += 1
  return clear, other, overcast

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)
clear, other, overcast = do('AMW')
ax.set_title("2011 - 6 AM Cloudiness for Ames")
ax.set_ylabel("Days for Ames")
ax.bar( numpy.arange(1,13)-0.4, clear, fc='b', label='Clear')
ax.bar( numpy.arange(1,13)-0.4, other, bottom=clear, fc='g', label='Broken')
ax.bar( numpy.arange(1,13)-0.4, overcast, bottom=(clear+other), fc='r', label='Overcast')
ax.set_xlim(0.5,11.5)
ax.set_xticks( numpy.arange(1,12) )
ax.set_xticklabels(('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov'))

ax = fig.add_subplot(212)
clear, other, overcast = do('DSM')
ax.set_ylabel("Days for Des Moines")
ax.bar( numpy.arange(1,13)-0.4, clear, fc='b', label='Clear')
ax.bar( numpy.arange(1,13)-0.4, other, bottom=clear, fc='g', label='Broken')
ax.bar( numpy.arange(1,13)-0.4, overcast, bottom=(clear+other), fc='r', label='Overcast')
ax.set_xlim(0.5,11.5)
ax.set_xticks( numpy.arange(1,12) )
ax.set_xticklabels(('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov'))
ax.legend(ncol=3, loc=(0.13,-0.25))

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
