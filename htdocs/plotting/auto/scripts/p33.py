import psycopg2.extras
import datetime
import pandas as pd
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents the largest drop in low
    temperature during a fall season.  The drop compares the lowest
    low previous to the date with the low for that date.  For example,
    if your coldest low to date was 40, you would not expect to see a
    low temperature of 20 the next night without first setting colder
    daily low temperatures."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    today = datetime.date.today()
    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    cursor.execute("""
      with data as (
        select day, year, month, low,
        min(low)
        OVER (ORDER by day ASC ROWS between 91 PRECEDING and 1 PRECEDING) as p
        from """ + table + """ where station = %s)

      SELECT year, max(p - low) from data
      WHERE month > 6 GROUP by year ORDER by year ASC
    """, (station,))

    years = []
    data = []
    rows = []
    for row in cursor:
        if row[0] == today.year:
            continue
        years.append(row[0])
        data.append(0-row[1])
        rows.append(dict(year=row[0], drop=row[1]))
    df = pd.DataFrame(rows)

    (fig, ax) = plt.subplots(1, 1, sharex=True)
    ax.bar(years, data, fc='b', ec='b')
    ax.grid(True)
    ax.set_ylabel("Largest Low Temp Drop $^\circ$F")
    ax.set_title(("%s %s\n"
                  "Max Jul-Dec Low Temp Drop Exceeding "
                  "Previous Min Low for Fall"
                  ) % (station, nt.sts[station]['name']))
    ax.set_xlim(min(years)-1, max(years)+1)

    return fig, df
