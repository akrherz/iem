import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)


from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
asos = i['asos']
import mx.DateTime
import numpy

data = {}
cnts = numpy.zeros( (2012-1971), 'f')
for yr in range(1971,2012):
    rs = asos.query("""SELECT valid, tmpf, dwpf from t%s 
        WHERE station = 'DSM' and tmpf > 0 and dwpf > 0 and extract(month from valid) = 7 
        ORDER by valid ASC""" % (yr,)).dictresult()
    for i in range(len(rs)):
        ts = mx.DateTime.strptime(rs[i]['valid'][:16], '%Y-%m-%d %H:%M')
        key = ts.strftime("%Y%m%d%H")
        if data.has_key(key):
            continue
        data[key] = 0
        h = mesonet.heatidx(rs[i]['tmpf'], mesonet.relh(rs[i]['tmpf'], rs[i]['dwpf']))
        if h >= 100:
            cnts[yr-1971] += 1

avgV = numpy.average(cnts)
bars = ax.bar( numpy.arange(1971,2012) -0.4, cnts , fc='r', ec='r')
ax.plot( [1971,2012], [avgV,avgV] )
for bar in bars:
    if bar.get_height() < avgV:
       bar.set_edgecolor('b')
       bar.set_facecolor('b')
#bars[-1].set_edgecolor("b")
#bars[-1].set_facecolor("b")
ax.set_ylabel("Hours over 100 F")
ax.set_xlim(1970.5,2011.5)
ax.set_ylim(0,5*24)
ax.set_yticks( numpy.arange(0,5*24,24) )
#ax.set_xlabel("*2011 Total thru 15 July")
ax.set_title("Des Moines *July* Hours over 100 F Heat Index [1971-2011]")
ax.grid(True)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
