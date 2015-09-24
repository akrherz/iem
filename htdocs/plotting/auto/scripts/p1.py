import psycopg2
import numpy as np
from scipy import stats
from pyiem import network
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['arguments'] = [
        dict(type='station', name='station', default='IA0000',
             label='Select Station'),
        dict(type='text', name='high', default='93',
             label='Daily High Temp Threshold'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor()

    station = fdict.get('station', 'IA0000')
    high = int(fdict.get('high', 93))
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))
    years = []
    rain = []
    temp = []
    ccursor.execute("""
  WITH precip as (
  SELECT year, sum(precip) * 25.4 as rain from """+table+""" where
  station = %s and month in (5,6) GROUP by year),
  temps as (
  SELECT year, sum(case when high > %s then 1 else 0 end) as t from
  """ + table + """
  WHERE station = %s and month in (7,8) GROUP by year)

  SELECT p.year, rain, t from precip p JOIN temps t on (t.year = p.year)
  WHERE t.year < extract(year from now())

    """, (station, high, station))
    for row in ccursor:
        years.append(row[0])
        temp.append(row[2])
        rain.append(row[1])
    df = pd.DataFrame(dict(year=pd.Series(years),
                           temp=pd.Series(temp),
                           precip=pd.Series(rain)))
    years = np.array(years)
    temp = np.array(temp)
    rain = np.array(rain)

    (fig, ax) = plt.subplots(1, 1)
    ax.scatter(rain, temp, marker='s', facecolor='b', edgecolor='b')
    ax.set_title(("1893-2013 %s [%s]\n"
                  "May-June Rainfall + July-August Hot Days (> %s$^\circ$F)"
                  ) % (nt.sts[station]['name'], station, high))
    ax.grid(True)

    h_slope, intercept, r_value, _, _ = stats.linregress(rain, temp)
    y = h_slope * np.arange(min(rain), max(rain)) + intercept
    ax.plot(np.arange(min(rain), max(rain)), y, lw=2, color='r',
            label="Slope=%.2f days/mm  R$^2$=%.2f" % (h_slope, r_value ** 2))
    ax.set_ylim(bottom=-1)
    ax.legend(fontsize=10)
    ax.set_xlim(left=0)
    ax.set_ylabel("Number July-August Days > %s$^\circ$F" % (high,))
    ax.set_xlabel("May-June Precipitation [mm]")

    return fig, df
