import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim(0,1440*3+2)
xticks = []
xticklabels = []
for x in range(0,73,6):
    xticks.append( x * 60 )
    if x % 24 == 0:
        lbl = 'Mid'
    elif x % 12 == 0:
        lbl = 'Noon'
    else:
        lbl = x % 12
    xticklabels.append(lbl)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlabel("Local Hour of Day [CDT]")
ax.set_ylabel("Heat Index [F]")


from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
asos = i['asos']
import mx.DateTime

events = 0
for yr in range(1949,2011):
    rs = asos.query("""SELECT valid, tmpf, dwpf from t%s 
        WHERE station = 'DSM' and tmpf > 0 and dwpf > 0 
        ORDER by valid ASC""" % (yr,)).dictresult()
    over105 = None
    for i in range(len(rs)):
        ts = mx.DateTime.strptime(rs[i]['valid'][:16], '%Y-%m-%d %H:%M')
        h = mesonet.heatidx(rs[i]['tmpf'], mesonet.relh(rs[i]['tmpf'], rs[i]['dwpf']))
        if h >= 105:
            if over105 is None:
                over105 = ts
        else:
            if over105 is not None:
                delta = (ts - over105).hours
                if delta >= 4:
                    events += 1
                    # We are ready to fetch data
                    yest = ts + mx.DateTime.RelativeDateTime(days=-1,hour=0,minute=0)
                    d2 = ts + mx.DateTime.RelativeDateTime(days=2)
                    rs2 = asos.query("""
                    SELECT valid, tmpf, dwpf from t%s WHERE station = 'DSM' and
                    tmpf > 0 and dwpf > 0 and valid >= '%s 00:00' 
                    and valid <= '%s 00:00' ORDER by valid ASC
                    """ % (ts.year, yest.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d"))).dictresult()
                    times = []
                    heat = []
                    for j in range(len(rs2)):
                        ts2 = mx.DateTime.strptime(rs2[j]['valid'][:16], '%Y-%m-%d %H:%M')
                        h2 = mesonet.heatidx(rs2[j]['tmpf'], mesonet.relh(rs2[j]['tmpf'], rs2[j]['dwpf']))
                        times.append( (ts2 - yest).hours * 60 + ts2.minute )
                        heat.append( h2 )
                    ax.plot(times, heat)
            over105 = None
ax.set_title("Des Moines Airport [1949-2010], Events %s\nDay before and day after a day of 4+ hours of 105+ Heat Index" % (events,))

ax.grid(True)
import iemplot
fig.savefig('test.png')
#iemplot.makefeature('test')