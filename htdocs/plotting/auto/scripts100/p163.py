"""LSR map by WFO"""
import datetime
from collections import OrderedDict

import psycopg2
import numpy as np
from pandas.io.sql import read_sql
import pytz
from pyiem.plot import MapPlot
from pyiem.util import get_autoplot_context

MDICT = OrderedDict([
 ('NONE', 'All LSR Types'),
 ('NRS', 'All LSR Types except HEAVY RAIN + SNOW'),
 ('CON', 'Convective LSRs (Tornado, TStorm Gst/Dmg, Hail)'),
 ("AVALANCHE", "AVALANCHE"),
 ("BLIZZARD", "BLIZZARD"),
 ("COASTAL FLOOD", "COASTAL FLOOD"),
 ("DEBRIS FLOW", "DEBRIS FLOW"),
 ("DENSE FOG", "DENSE FOG"),
 ("DOWNBURST", "DOWNBURST"),
 ("DUST STORM", "DUST STORM"),
 ("EXCESSIVE HEAT", "EXCESSIVE HEAT"),
 ("EXTREME COLD", "EXTREME COLD"),
 ("EXTR WIND CHILL", "EXTR WIND CHILL"),
 ("FLASH FLOOD", "FLASH FLOOD"),
 ("FLOOD", "FLOOD"),
 ("FOG", "FOG"),
 ("FREEZE", "FREEZE"),
 ("FREEZING DRIZZLE", "FREEZING DRIZZLE"),
 ("FREEZING RAIN", "FREEZING RAIN"),
 ("FUNNEL CLOUD", "FUNNEL CLOUD"),
 ("HAIL", "HAIL"),
 ("HEAVY RAIN", "HEAVY RAIN"),
 ("HEAVY SLEET", "HEAVY SLEET"),
 ("HEAVY SNOW", "HEAVY SNOW"),
 ("HIGH ASTR TIDES", "HIGH ASTR TIDES"),
 ("HIGH SURF", "HIGH SURF"),
 ("HIGH SUST WINDS", "HIGH SUST WINDS"),
 ("HURRICANE", "HURRICANE"),
 ("ICE STORM", "ICE STORM"),
 ("LAKESHORE FLOOD", "LAKESHORE FLOOD"),
 ("LIGHTNING", "LIGHTNING"),
 ("LOW ASTR TIDES", "LOW ASTR TIDES"),
 ("MARINE TSTM WIND", "MARINE TSTM WIND"),
 ("NON-TSTM WND DMG", "NON-TSTM WND DMG"),
 ("NON-TSTM WND GST", "NON-TSTM WND GST"),
 ("RAIN", "RAIN"),
 ("RIP CURRENTS", "RIP CURRENTS"),
 ("SLEET", "SLEET"),
 ("SNOW", "SNOW"),
 ("STORM SURGE", "STORM SURGE"),
 ("TORNADO", "TORNADO"),
 ("TROPICAL STORM", "TROPICAL STORM"),
 ("TSTM WND DMG", "TSTM WND DMG"),
 ("TSTM WND GST", "TSTM WND GST"),
 ("WALL CLOUD", "WALL CLOUD"),
 ("WATER SPOUT", "WATER SPOUT"),
 ("WILDFIRE", "WILDFIRE")])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This application generates a map displaying the
    number of LSRs issued between a period of your choice by NWS Office."""
    today = datetime.date.today()
    jan1 = today.replace(month=1, day=1)
    desc['arguments'] = [
        dict(type='datetime', name='sdate',
             default=jan1.strftime("%Y/%m/%d 0000"),
             label='Start Date / Time (UTC, inclusive):',
             min="2006/01/01 0000"),
        dict(type='datetime', name='edate',
             default=today.strftime("%Y/%m/%d 0000"),
             label='End Date / Time (UTC):',
             min="2006/01/01 0000"),
        dict(type='select', name='filter', default='NONE', options=MDICT,
             label='Local Storm Report Type Filter'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    sts = ctx['sdate']
    sts = sts.replace(tzinfo=pytz.utc)
    ets = ctx['edate']
    ets = ets.replace(tzinfo=pytz.utc)
    myfilter = ctx['filter']
    if myfilter == 'NONE':
        tlimiter = ''
    elif myfilter == 'NRS':
        tlimiter = " and typetext not in ('HEAVY RAIN', 'SNOW', 'HEAVY SNOW') "
    elif myfilter == 'CON':
        tlimiter = (" and typetext in ('TORNADO', 'HAIL', 'TSTM WND GST', "
                    "'TSTM WND DMG') ")
    else:
        tlimiter = " and typetext = '%s' " % (myfilter,)

    df = read_sql("""
    SELECT wfo, count(*) from lsrs
    WHERE valid >= %s and valid < %s """ + tlimiter + """
    GROUP by wfo ORDER by wfo ASC
    """, pgconn, params=(sts, ets), index_col='wfo')
    data = {}
    for wfo, row in df.iterrows():
        data[wfo] = row['count']
    maxv = df['count'].max()
    bins = np.linspace(0, maxv, 12, dtype='i')
    bins[-1] += 1
    p = MapPlot(sector='nws', axisbg='white',
                title='Local Storm Report Counts by NWS Office',
                subtitlefontsize=10,
                subtitle=('Valid %s - %s UTC, type limiter: %s'
                          ) % (sts.strftime("%d %b %Y %H:%M"),
                               ets.strftime("%d %b %Y %H:%M"),
                               MDICT.get(myfilter)))
    p.fill_cwas(data, bins=bins, ilabel=True)

    return p.fig, df


if __name__ == '__main__':
    plotter(dict())
