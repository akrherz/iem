import psycopg2.extras
import numpy as np
from pyiem.network import Table as NetworkTable
import datetime
import pandas as pd
import calendar

PDICT = {'max_tmpf': 'High Temperature',
         'min_tmpf': 'Low Temperature',
         'pday': 'Precipitation'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart presents a series of daily summary data
    as a calendar.  The daily totals should be valid for the local day of the
    weather station.
    """
    today = datetime.date.today()
    m90 = today - datetime.timedelta(days=90)
    d['arguments'] = [
        dict(type='zstation', name='station', default='DSM',
             label='Select Station'),
        dict(type='select', name='var', default='pday',
             label='Which Daily Variable:', options=PDICT),
        dict(type='date', name='sdate',
             default=m90.strftime("%Y/%m/%d"),
             label='Start Date:', min="2010/01/01"),
        dict(type='date', name='edate',
             default=today.strftime("%Y/%m/%d"),
             label='End Date:', min="2010/01/01"),
    ]
    return d


def safe(row, varname):
    val = row[varname]
    if varname == 'pday':
        if val == 0.0001:
            return 'T'
        return "%.2f" % (val,)
    return '%.0f' % (val,)


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import calendar_plot
    pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'DSM')
    varname = fdict.get('var', 'pday')
    network = fdict.get('network', 'IA_ASOS')
    sdate = datetime.datetime.strptime(fdict.get('sdate', '2015-01-01'),
                                       '%Y-%m-%d')
    edate = datetime.datetime.strptime(fdict.get('edate', '2015-02-01'),
                                       '%Y-%m-%d')
    sdate = sdate.date()
    edate = edate.date()
    if PDICT.get(varname) is None:
        return

    nt = NetworkTable(network)

    cursor.execute("""
    SELECT day, max_tmpf, min_tmpf, pday from summary s JOIN stations t
    on (t.iemid = s.iemid) WHERE s.day >= %s and s.day <= %s and
    t.id = %s and t.network = %s ORDER by day ASC
    """, (sdate, edate, station, network))
    rows = []
    data = {}
    for row in cursor:
        data[row[0]] = {'val': safe(row, varname)}
        rows.append(dict(day=row['day'], max_tmpf=row['max_tmpf'],
                         min_tmpf=row['min_tmpf'], pday=row['pday']))
    df = pd.DataFrame(rows)

    title = '[%s] %s Daily %s' % (station, nt.sts[station]['name'],
                                PDICT.get(varname))

    fig = calendar_plot(sdate, edate, data,
                        title=title)
    return fig, df
