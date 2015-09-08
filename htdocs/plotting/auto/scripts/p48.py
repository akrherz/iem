import psycopg2.extras
import pyiem.nws.vtec as vtec
import numpy as np


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['description'] = """For a given watch/warning/advisory type and forecast
    zone, what is the frequency by time of day that the product was valid.  The
    total number of events for the county/zone is used for the frequency."""
    d['arguments'] = [
        dict(type='ugc', name='ugc',
             default='IAZ048', label='Select UGC Zone/County:'),
        dict(type='phenomena', name='phenomena',
             default='WC', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='W', label='Select Watch/Warning Significance Level:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    ugc = fdict.get('ugc', 'IAZ048')
    phenomena = fdict.get('phenomena', 'WC')
    significance = fdict.get('significance', 'W')

    (fig, ax) = plt.subplots(1, 1)

    cursor.execute("""
    SELECT s.wfo, s.tzname, u.name from ugcs u
    JOIN stations s on (u.wfo = s.id)
    where ugc = %s and end_ts is null and s.network = 'WFO'
    """, (ugc,))
    wfo = None
    tzname = None
    name = ""
    if cursor.rowcount == 1:
        row = cursor.fetchone()
        tzname = row[1]
        wfo = row[0]
        name = row[2]

    cursor.execute("""
     SELECT count(*), min(issue at time zone %s), max(issue at time zone %s)
     from warnings WHERE ugc = %s and phenomena = %s and significance = %s
     and wfo = %s
    """, (tzname, tzname, ugc, phenomena, significance, wfo))
    row = cursor.fetchone()
    cnt = row[0]
    sts = row[1]
    ets = row[2]
    if sts is None:
        ax.text(0.5, 0.5, "No Results Found, try flipping zone/county",
                transform=ax.transAxes, ha='center')
        return fig

    cursor.execute("""
     WITH coverage as (
        SELECT extract(year from issue) as yr, eventid,
        generate_series(issue at time zone %s,
                        expire at time zone %s, '1 minute'::interval) as s
                        from warnings where
        ugc = %s and phenomena = %s and significance = %s and wfo = %s),
      minutes as (SELECT distinct yr, eventid,
        (extract(hour from s)::numeric * 60. +
         extract(minute from s)::numeric) as m
        from coverage)

    SELECT minutes.m, count(*) from minutes GROUP by m
          """, (tzname, tzname, ugc, phenomena, significance, wfo))

    data = np.zeros((1440,), 'f')
    for row in cursor:
        data[int(row[0])] = row[1]

    ax.bar(np.arange(1440), data / float(cnt) * 100., ec='b', fc='b')
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.grid()
    ax.set_xticks(range(0, 1440, 60))
    ax.set_xticklabels(["Mid", "", "", "3 AM", "", "", "6 AM", "", "", '9 AM',
                        "", "", "Noon", "", "", "3 PM", "", "", "6 PM",
                        "", "", "9 PM", "", "", "Mid"])
    ax.set_xlabel("Timezone: %s (Daylight or Standard)" % (tzname,))
    ax.set_ylabel("Frequency [%%] out of %s Events" % (cnt,))
    ax.set_title(("[%s] %s :: %s %s (%s.%s)\n%s Events - %s to %s"
                  ) % (ugc, name, vtec._phenDict[phenomena],
                       vtec._sigDict[significance],
                       phenomena, significance, cnt,
                       sts.strftime("%Y-%m-%d %I:%M %p"),
                       ets.strftime("%Y-%m-%d %I:%M %p")))
    ax.set_xlim(0, 1441)
    return fig
