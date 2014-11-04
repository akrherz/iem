"""
  Fall Minimum by Date
"""
import psycopg2.extras
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import datetime
import calendar
from pyiem.network import Table as NetworkTable

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200', 
             label='Select Station:'),
    ]
    return d


def plotter( fdict ):
    """ Go """
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    
    cursor.execute("""
      with data as (
        select day, year, month, low, 
        min(low) OVER (ORDER by day ASC ROWS between 91 PRECEDING and 1 PRECEDING) as p 
        from """+table+""" where station = %s) 

      SELECT year, max(p - low) from data 
      WHERE month > 6 GROUP by year ORDER by year ASC
    """, (station,))

    years = []
    data = []
    for row in cursor:
        years.append(row[0])
        data.append(0-row[1])
    
    (fig, ax) = plt.subplots(1,1, sharex=True)
    bars = ax.bar(years, data,  fc='b', ec='b')
    ax.grid(True)
    ax.set_ylabel("Largest Low Temp Drop $^\circ$F")
    ax.set_title("%s %s\nMax Jul-Dec Low Temp Drop Exceeding Previous Min Low for Fall" % (station, 
                                        nt.sts[station]['name']))
    ax.set_xlim(min(years)-1,max(years)+1)


    return fig
