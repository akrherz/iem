import matplotlib.pyplot as plt
import psycopg2.extras
import numpy as np
from pyiem import network
import calendar

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200', label='Select Station:'),
        dict(type='text', name='syear', default='1993', label='Enter Start Year:'),
        dict(type='text', name='eyear', default='2013', label='Enter End Year (inclusive):'),
        dict(type='text', name='threshold', default='80', label='Threshold Percentage [%]:'),
    ]
    return d

def plotter( fdict ):
    """ Go """
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    syear = int(fdict.get('syear', 1993))
    eyear = int(fdict.get('eyear', 2013))
    threshold = int(fdict.get('threshold', 80))

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
    with months as (
      select year, month, p, avg(p) OVER (PARTITION by month) from (
        select year, month, sum(precip) as p from """+table+""" 
        where station = %s and year < extract(year from now()) 
        GROUP by year, month) as foo) 
        
    SELECT month, sum(case when p > (avg * %s / 100.0) then 1 else 0 end) 
    from months WHERE year >= %s and year < %s 
    GROUP by month ORDER by month ASC
    """, (station, threshold, syear, eyear))
    vals = []
    years = float(1 + eyear - syear)
    for row in ccursor:
        vals.append( row[1] / years * 100.)

    (fig, ax) = plt.subplots(1,1)

    ax.bar(np.arange(1,13)-0.4, vals)
    ax.set_xticks( np.arange(1,13) )
    ax.set_ylim(0,100)
    ax.set_yticks(np.arange(0,101,10))
    ax.set_xticklabels( calendar.month_abbr[1:13] )
    ax.grid(True)
    ax.set_xlim(0.5, 12.5)
    ax.set_ylabel("Percentage of Months, n=%.0f years" % (years,))
    ax.set_title(("%s [%s] Monthly Precipitation Reliability\n"
                  +"Period: %s-%s, %% of Months above %s%% of Long Term Avg") % (
                                nt.sts[station]['name'], station, syear,
                                eyear, threshold))
        
    return fig
