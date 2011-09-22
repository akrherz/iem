import mx.DateTime
import numpy as np
import pg
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

asos = pg.connect("asos", 'iemdb', user='nobody')
coop = pg.connect('coop', 'iemdb', user='nobody')

clear = np.zeros( (366,) )
clear_abovenormal = np.zeros( (366,) )
southwinds = np.zeros( (366,) )
southwinds_abovenormal = np.zeros( (366,) )
both_abovenormal = np.zeros( (366,) )
days = np.zeros( (366,) )
abovenormal = np.zeros( (366,) )


def smooth(x,window_len=11,window='hanning'):
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=np.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]


obs = {}
rs = coop.query("""
select o.day, extract(doy from day) as doy, o.high - c.high as diff from alldata o, climate c where 
    c.station = 'ia2203' and o.stationid = 'ia2203' 
    and o.sday = to_char(c.valid, 'mmdd') and o.day > '1972-12-31'
""").dictresult()
for row in rs:
    obs[ row['day'] ] = row['diff']
    days[ int(row['doy']) - 1] += 1


# Get ASOS data
rs = asos.query("""
  SELECT date(valid) as d, count(*), sum( case when skyc1 in ('BKN','OVC') 
      or skyc2 in ('BKN','OVC') or skyc3 in ('BKN','OVC') then 1 else 0 end ) as clouds,
    sum( case when sknt >= 7 and (drct > 270 or drct < 90) then 1 else 0 end ) as southwinds
  ,max(tmpf) as high from alldata WHERE station = 'DSM' and valid > '1973-01-01' and valid < 'TODAY'
  and extract(hour from valid) between 7 and 19 GROUP by d
    """).dictresult()
for row in rs:
    # Not enough obs
    if row['count'] < 6:
        continue
    day = mx.DateTime.strptime(row['d'], '%Y-%m-%d')
    if row['clouds'] < 4 and obs[ row['d'] ] < -5.:
        clear_abovenormal[ int(day.strftime("%j")) - 1 ] += 1
    if row['clouds'] < 4:
        clear[ int(day.strftime("%j")) - 1 ] += 1
    if row['southwinds'] > 2 and obs[ row['d'] ] < -5.:
        southwinds_abovenormal[ int(day.strftime("%j")) - 1 ] += 1
    if row['clouds'] < 4 and row['southwinds'] > 2 and obs[ row['d'] ] < -5.:
        both_abovenormal[ int(day.strftime("%j")) - 1 ] += 1
    if row['southwinds'] > 2:
        southwinds[ int(day.strftime("%j")) - 1 ] += 1
    if obs[ row['d'] ] < -5.:
        abovenormal[ int(day.strftime("%j")) - 1 ] += 1
    
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

#ax.plot( np.arange(366), clear, label='Coldest')
ax.plot( np.arange(365), smooth(clear_abovenormal[:365] / abovenormal[:365],14,'hamming') * 100., label='Mostly Clear Skies')
ax.plot( np.arange(365), smooth(southwinds_abovenormal[:365] / abovenormal[:365],14, 'hamming') * 100., label='North Winds')
#ax.plot( np.arange(365), smooth(both_abovenormal[:365] / abovenormal[:365],7, 'hamming') * 100., label='Both')
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlabel("Des Moines 8AM-6PM [1973-2011]")
ax.set_ylabel("Observed Frequency [%]")
ax.set_ylim(0,100)
ax.set_yticks([0,20,40,50,60,80,100])
ax.set_title("When High Temp was at least 5$^{\circ}\mathrm{F}$ Below Average\nwere daytime northerly winds or mostly clear skies observed?")
ax.grid(True)
ax.set_xlim(0,360)

ax.legend(loc=2,prop=prop)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')