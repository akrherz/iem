import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This table presents the 10 largest differences
    between the lowest and highest air temperature for a local calendar
    day."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    font0 = FontProperties()
    font0.set_family('monospace')
    font0.set_size(16)
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')

    nt = NetworkTable(network)

    df = read_sql("""WITH data as (
        SELECT date(valid at time zone %s) as date, max(tmpf), min(tmpf)
        from alldata where station = %s and tmpf between -100 and 150
        GROUP by date)

    SELECT date, min, max, max - min as difference from data
    ORDER by difference DESC, date DESC LIMIT 10
        """, pgconn, params=(nt.sts[station]['tzname'], station),
                  parse_dates=('date',), index_col=None)
    df['rank'] = df['difference'].rank(ascending=False, method='min')
    fig = plt.figure(figsize=(5.5, 4))
    fig.text(0.5, 0.9, ("%s [%s] %s-%s\n"
                        "Top 10 Local Calendar Day Temperature Differences"
                        ) % (nt.sts[station]['name'], station,
                             nt.sts[station]['archive_begin'].year,
                             datetime.date.today().year), ha='center')
    fig.text(0.1, 0.81, " #  Date         Diff   Low High",
             fontproperties=font0)
    y = 0.74
    for _, row in df.iterrows():
        fig.text(0.1, y, ("%2.0f  %11s   %3.0f   %3.0f  %3.0f"
                          ) % (row['rank'], row['date'].strftime("%d %b %Y"),
                               row['difference'], row['min'], row['max']),
                 fontproperties=font0)
        y -= 0.07
    return fig, df

if __name__ == '__main__':
    plotter(dict())
