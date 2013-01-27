import iemdb
import math
import iemtz
import numpy
HADS = iemdb.connect('hads', bypass=True)
hcursor = HADS.cursor()

def uv(sped, drct2):
    dirr = drct2 * math.pi / 180.00
    s = numpy.sin(dirr)
    c = numpy.cos(dirr)
    u = - sped * s
    v = - sped * c
    return u, v


hcursor.execute("""
 select valid, key, value from raw2012_12 where station = 'SAYI4' 
 and key in ('HPIRGZ', 'UDIRGZ', 'USIRGZ') and valid > '2012-12-07 23:30' 
 ORDER by valid ASC
""")
valid = {'HPIRGZ': [], 'UDIRGZ': [], 'USIRGZ': []}
values = {'HPIRGZ': [], 'UDIRGZ': [], 'USIRGZ': []}
for row in hcursor:
    valid[row[1]].append( row[0] )
    values[row[1]].append( row[2] )

u, v = uv( numpy.array(values['USIRGZ']), numpy.array(values['UDIRGZ']))

hcursor.execute("""
 select valid, key, value from raw2012_03 where station = 'SAYI4' 
 and key in ('HPIRGZ', 'UDIRGZ', 'USIRGZ') and valid > '2012-03-05 23:30'
 and valid < '2012-03-08 22:00' 
 ORDER by valid ASC
""")
valid2 = {'HPIRGZ': [], 'UDIRGZ': [], 'USIRGZ': []}
values2 = {'HPIRGZ': [], 'UDIRGZ': [], 'USIRGZ': []}
for row in hcursor:
    valid2[row[1]].append( row[0] )
    values2[row[1]].append( row[2] )

u2, v2 = uv( numpy.array(values2['USIRGZ']), numpy.array(values2['UDIRGZ']))

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker
import matplotlib.transforms as transforms
import matplotlib.patches as patches

(fig, ax) = plt.subplots(2,1, figsize=(5,8))

def getcolor(s):
    if s > 20:
        return 'r'
    if s > 10:
        return 'g'
    else:
        return 'k'

ax2 = ax[0].twinx()

rect = patches.Rectangle((0.55,0), width=0.3, height=1,
                         transform=ax2.transAxes, color='tan',
                         alpha=0.5, zorder=1)
ax[0].add_patch(rect)
ax2.text(0.6, 0.8 , "NW Winds push\nwater to gauge", transform=ax2.transAxes)

ax[0].plot( valid['HPIRGZ'], values['HPIRGZ'], zorder=2)


dt = (valid['USIRGZ'][-1] - valid['USIRGZ'][0]).days * 86400.0 + (valid['USIRGZ'][-1] - valid['USIRGZ'][0]).seconds
    


normal = 300.0
skip = 0
for ts,s,du,dv in zip(valid['USIRGZ'], values['USIRGZ'], u, v):
    if skip % 3 == 0:
        x = ((ts - valid['USIRGZ'][0]).days * 86400.0 + (ts - valid['USIRGZ'][0]).seconds) / dt

        ax2.arrow(x, 0.2, du / normal, dv / normal , head_width=0.015, 
                  color=getcolor(s), transform=ax2.transAxes, zorder=2)
    skip += 1

ax2.arrow( 0.1, 0.9, 20.0 / normal, 0, head_width=0.015, color=getcolor(20.1),
           transform=ax2.transAxes, zorder=2)
ax2.text( 0.15, 0.92, "20+ MPH", color=getcolor(20.1),
           transform=ax2.transAxes, zorder=2)

ax2.arrow( 0.1, 0.8, 10.0 / normal, 0, head_width=0.015, color=getcolor(10.1),
           transform=ax2.transAxes, zorder=2)
ax2.text( 0.15, 0.82, "10+ MPH", color=getcolor(10.1),
           transform=ax2.transAxes, zorder=2)

ax2.arrow( 0.1, 0.7, 8.0 / normal, 0, head_width=0.015, color=getcolor(8.1),
           transform=ax2.transAxes, zorder=2)
ax2.text( 0.15, 0.72, "<10 MPH", color=getcolor(8.1),
           transform=ax2.transAxes, zorder=2)

ax2.set_ylim(min(valid['HPIRGZ']) , max(valid['HPIRGZ']) )

ax[0].xaxis.set_major_locator(
                               mdates.DayLocator(interval=1,
                                                 tz=iemtz.Central)
                               )
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%Y',
                                                      tz=iemtz.Central))
ax[0].yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax[0].yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.2f'))

ax[0].set_xlim(min(valid['HPIRGZ']) , max(valid['HPIRGZ']) )
ax[0].set_ylim(min(values['HPIRGZ'])-0.1, max(values['HPIRGZ'])+0.1)
ax[0].grid(True)
ax[0].set_title("Saylorville Lake (SAYI4) Wind Driven Water")
ax[0].set_ylabel("Reserviour Height (ft)")


ax3 = ax[1].twinx()

rect = patches.Rectangle((0.10,0), width=0.40, height=1,
                         transform=ax3.transAxes, color='tan',
                         alpha=0.5, zorder=1)
ax[1].add_patch(rect)

ax3.text(0.15, 0.8 , "SE Winds push\nwater away from gauge", transform=ax3.transAxes)


ax[1].plot( valid2['HPIRGZ'], values2['HPIRGZ'], zorder=2)


dt = (valid2['USIRGZ'][-1] - valid2['USIRGZ'][0]).days * 86400.0 + (valid2['USIRGZ'][-1] - valid2['USIRGZ'][0]).seconds
    
normal = 300.0
skip = 0
for ts,s,du,dv in zip(valid2['USIRGZ'], values2['USIRGZ'], u2, v2):
    x = ((ts - valid2['USIRGZ'][0]).days * 86400.0 + (ts - valid2['USIRGZ'][0]).seconds) / dt
    if skip % 3 == 0:
        print x, du, dv
        ax3.arrow(x, 0.2, du / normal, dv / normal , head_width=0.015, 
                  color=getcolor(s), transform=ax3.transAxes, zorder=2)
    skip += 1

ax[1].set_xlim(min(valid2['HPIRGZ']) , max(valid2['HPIRGZ']) )
ax[1].set_ylim(min(values2['HPIRGZ'])-0.1, max(values2['HPIRGZ'])+0.1)
ax[1].xaxis.set_major_locator(
                               mdates.DayLocator(interval=1,
                                                 tz=iemtz.Central)
                               )
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%Y',
                                                      tz=iemtz.Central))
ax[1].yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax[1].yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.2f'))
ax[1].set_ylabel("Reserviour Height (ft)")
ax3.set_ylim(min(valid2['HPIRGZ']) , max(valid2['HPIRGZ']) )

ax3.yaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
ax2.yaxis.set_major_formatter(matplotlib.ticker.NullFormatter())

ax[1].grid(True)

fig.tight_layout()

fig.savefig('121211.ps')
#import iemplot
#iemplot.makefeature('test')
