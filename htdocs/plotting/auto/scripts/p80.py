import psycopg2.extras
import pyiem.nws.vtec as vtec
import numpy as np
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot presents the accumulated frequency of
    duration for a given NWS VTEC Watch, Warning, Advisory product."""
    d['arguments'] = [
        dict(type='ugc', name='ugc',
             default='IAC153', label='Select UGC Zone/County:'),
        dict(type='phenomena', name='phenomena',
             default='TO', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='A', label='Select Watch/Warning Significance Level:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    ugc = fdict.get('ugc', 'IAC153')
    phenomena = fdict.get('phenomena', 'TO')
    significance = fdict.get('significance', 'A')

    (fig, ax) = plt.subplots(1, 1)

    cursor.execute("""
    SELECT s.wfo, s.tzname, u.name from ugcs u  JOIN stations s
    on (u.wfo = s.id)
    where ugc = %s and end_ts is null and s.network = 'WFO'
    """, (ugc,))
    wfo = None
    name = ""
    if cursor.rowcount == 1:
        row = cursor.fetchone()
        wfo = row[0]
        name = row[2]

    cursor.execute("""
     SELECT expire - issue, init_expire - issue, issue at time zone 'UTC'
     from warnings WHERE ugc = %s and phenomena = %s and significance = %s
     and wfo = %s and expire > issue and init_expire > issue
    """, (ugc, phenomena, significance, wfo))
    if cursor.rowcount < 2:
        ax.text(0.5, 0.5, "No Results Found, try flipping zone/county",
                transform=ax.transAxes, ha='center')
        return fig

    rows = []
    for row in cursor:
        rows.append(dict(final=row[0].total_seconds() / 60.,
                         initial=row[1].total_seconds() / 60.,
                         issue=row[2]))

    df = pd.DataFrame(rows)
    titles = {'initial': 'Initial Issuance',
              'final': 'Final Duration'}
    for col in ['final', 'initial']:
        sortd = df.sort_values(by=col)
        x = []
        y = []
        i = 0
        for _, row in sortd.iterrows():
            i += 1
            if i == 1:
                x.append(row[col])
                y.append(i)
                continue
            if x[-1] == row[col]:
                y[-1] = i
                continue
            y.append(i)
            x.append(row[col])

        ax.plot(x, np.array(y) / float(y[-1]) * 100., lw=2, label=titles[col])
    ax.grid()
    ax.legend(loc=2, ncol=2, fontsize=12)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    if x[-1] < 120:
        xmax = x[-1] + 10 - (x[-1] % 10)
        ax.set_xlim(0, xmax)
        ax.set_xticks(np.arange(0, xmax+1, 10))
        ax.set_xlabel("Duration [minutes]")
    else:
        xmax = x[-1] + 60 - (x[-1] % 60)
        ax.set_xlim(0, xmax)
        ax.set_xticks(np.arange(0, xmax+1, 60))
        ax.set_xticklabels(np.arange(0, (xmax+1)/60))
        ax.set_xlabel("Duration [hours]")
    ax.set_ylabel("Frequency [%%] out of %s Events" % (y[-1],))
    ax.set_title(("[%s] %s :: %s %s (%s.%s)\n"
                  "Distribution of Event Time Duration %s-%s"
                  ) % (ugc, name, vtec._phenDict[phenomena],
                       vtec._sigDict[significance],
                       phenomena, significance,
                       min(df['issue']).strftime("%-d %b %Y"),
                       max(df['issue']).strftime("%-d %b %Y")))

    return fig, df
