"""Calendar of SPC Outlooks by WFO/state."""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot import calendar_plot
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {
    'C': 'Convective',
    'F': 'Fire Weather',
}
PDICT2 = {'wfo': 'Summarize by Selected WFO',
          'state': 'Summarize by Selected State'}
COLORS = {
    'TSTM': "#c0e8c0",
    'MRGL': "#66c57d",
    'SLGT': "#f6f67b",
    'ENH': "#edbf7c",
    'MDT': "#f67a7d",
    'HIGH': "#ff78ff",

    'ELEV': '#ffbb7c',
    'CRIT': '#ff787d',
    'EXTM': '#ff78ff',
}
DAYS = OrderedDict((
  ("1", 'Day 1'),
  ("2", 'Day 2'),
  ("3", 'Day 3'),
  ("4", 'Day 4'),
  ("5", 'Day 5'),
  ("6", 'Day 6'),
  ("7", 'Day 7'),
  ("8", 'Day 8'),
))


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This application presents a calendar of Storm
    Prediction Center outlooks by state or WFO.  The GIS spatial operation
    done is a simple touches.  So an individual outlook that just barely
    scrapes a state or CWA would count for this presentation.  Suggestions
    would be welcome as to how this could be improved.

    <p>This app attempts to not double-count outlook days by not considering
    the midnight to 12z period that a given outlook could be valid for a given
    date.  This likely sounds confusing.  For example, SPC issues a new Day
    1 slight risk with their 8 PM update.  This new slight risk is technically
    valid into the next day, but is only considered for the calendar day that
    the 8 PM update was issued on.  This logic is what people want to see
    presented here, but is not 100% accurate for outlooks per calendar day.</p>
    """
    today = datetime.date.today()
    jan1 = today.replace(month=1, day=1)
    desc['arguments'] = [
        dict(type='date', name='sdate',
             default=jan1.strftime("%Y/%m/%d"),
             label='Start Date (inclusive):',
             min="2002/01/01"),
        dict(type='date', name='edate',
             default=today.strftime("%Y/%m/%d"),
             label='End Date (inclusive):',
             min="2002/01/01"),
        dict(type='select', name='outlook_type', options=PDICT, default='C',
             label='Select Outlook Type'),
        dict(type='select', name='day', options=DAYS, default="1",
             label='Select Day Outlook'),
        dict(type='select', name='w', options=PDICT2, default='wfo',
             label='How to summarize data:'),
        dict(type='networkselect', name='wfo', network='WFO',
             default='DMX', label='Select WFO (when appropriate):'),
        dict(type='state', name='state',
             default='IA', label='Select State (when appropriate):'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('postgis')
    ctx = get_autoplot_context(fdict, get_description())
    sts = ctx['sdate']
    ets = ctx['edate']
    wfo = ctx['wfo']
    outlook_type = ctx['outlook_type']
    day = ctx['day']

    if ctx['w'] == 'wfo':
        table = "cwa"
        abbrcol = "wfo"
        geoval = wfo
    else:
        table = "states"
        abbrcol = "state_abbr"
        geoval = ctx['state']

    df = read_sql("""
    with data as (
        select expire, o.threshold from spc_outlooks o, """ + table + """ t
        WHERE t.""" + abbrcol + """ = %s and category = %s
        and ST_Overlaps(st_buffer(o.geom, 0), t.the_geom)
        and o.day = %s and o.outlook_type = %s and expire > %s
        and expire < %s),
    agg as (
        select date(expire - '1 day'::interval), d.threshold, priority,
        rank() OVER (PARTITION by date(expire - '1 day'::interval)
        ORDER by priority DESC)
        from data d JOIN spc_outlook_thresholds t
        on (d.threshold = t.threshold))

    SELECT distinct date, threshold from agg where rank = 1 ORDER by date ASC
    """, pgconn, params=(
        geoval,
        'CATEGORICAL' if outlook_type == 'C' else 'FIRE WEATHER CATEGORICAL',
        day, outlook_type, sts, ets + datetime.timedelta(days=2)),
                  index_col='date')

    data = {}
    now = sts
    while now <= ets:
        data[now] = {'val': " "}
        now += datetime.timedelta(days=1)
    for date, row in df.iterrows():
        data[date] = {
            'val': row['threshold'],
            'cellcolor': COLORS.get(row['threshold'], '#EEEEEE')
        }
    fig = calendar_plot(sts, ets, data)
    if ctx['w'] == 'wfo':
        nt = NetworkTable("WFO")
        title2 = "NWS %s [%s]" % (nt.sts[wfo]['name'], wfo)
    else:
        title2 = state_names[ctx['state']]
    fig.text(0.5, 0.95,
             ("SPC Day %s %s for %s by Calendar Date"
              "\nValid %s - %s"
              ) % (day, PDICT[outlook_type], title2,
                   sts.strftime("%d %b %Y"), ets.strftime("%d %b %Y")),
             ha='center', va='center')

    return fig, df


if __name__ == '__main__':
    plotter(dict(state='IA', w='state', sdate='2019-01-01',
                 edate='2019-04-15'))
