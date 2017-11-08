"""Flash Flood Guidance Plots"""
import datetime
from collections import OrderedDict

import pytz
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot import MapPlot

HOURS = OrderedDict([
    ('1', 'One Hour'),
    ('3', 'Three Hour'),
    ('6', 'Six Hour'),
    ('24', 'Twenty Four Hour')])
PDICT = {'cwa': 'Plot by NWS Forecast Office',
         'midwest': 'Midwestern US',
         'conus': 'Continental US',
         'state': 'Plot by State'}
PDICT3 = {'yes': 'YES: Label Counties/Zones',
          'no': 'NO: Do not Label Counties/Zones'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This application plots Flash Flood Guidance for
    a time of your choice.  The time is used to query a 24 hour trailing window
    to find the most recent FFG issuance for the counties/zones of interest.
    This dataset is based on IEM processing of county/zone based FFG guidance
    found in the FFG text products.
    """
    now = datetime.datetime.utcnow()
    desc['arguments'] = [
        dict(type='select', name='t', default='state', options=PDICT,
             label='Select plot extent type:'),
        dict(type='networkselect', name='wfo', network='WFO',
             default='DMX', label='Select WFO: (ignored if plotting state)'),
        dict(type='state', name='state',
             default='IA', label='Select State: (ignored if plotting wfo)'),
        dict(type='select', name='hour', default='1', options=HOURS,
             label='Guidance Period:'),
        dict(type='select', name='ilabel', default='yes', options=PDICT3,
             label='Overlay values on map?'),
        dict(type='datetime', name='ts',
             default=now.strftime("%Y/%m/%d %H%M"),
             label='Valid Time (UTC Timezone):', min="2003/01/01 0000"),
        ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib.pyplot as plt
    ctx = get_autoplot_context(fdict, get_description())
    ts = ctx['ts'].replace(tzinfo=pytz.utc)
    hour = int(ctx['hour'])
    ilabel = (ctx['ilabel'] == 'yes')
    column = "hour%02i" % (hour,)
    pgconn = get_dbconn('postgis')
    df = read_sql("""
    WITH data as (
        SELECT ugc, rank() OVER (PARTITION by ugc ORDER by valid DESC),
        hour01, hour03, hour06, hour12, hour24
        from ffg WHERE valid >= %s and valid <= %s)
    SELECT *, substr(ugc, 3, 1) as ztype from data where rank = 1
    """, pgconn, params=(ts - datetime.timedelta(hours=24), ts),
                  index_col='ugc')
    plot = MapPlot(sector=ctx['t'], continentalcolor='white',
                   state=ctx['state'], cwa=ctx['wfo'],
                   title=("NWS RFC %s Hour Flash Flood Guidance on "
                          "%s UTC"
                          ) % (hour, ts.strftime("%-d %b %Y %H")),
                   subtitle=("Estimated amount of %s Rainfall "
                             "needed for non-urban Flash Flooding to commence"
                             ) % (HOURS[ctx['hour']], ))
    bins = [0.01, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.25, 2.5, 2.75, 3.,
            3.5, 4.0, 5.0]
    cmap = plt.get_cmap('gist_rainbow_r')
    df2 = df[df['ztype'] == 'C']
    plot.fill_ugcs(df2[column].to_dict(), bins, cmap=cmap, plotmissing=False,
                   ilabel=ilabel)
    df2 = df[df['ztype'] == 'Z']
    plot.fill_ugcs(df2[column].to_dict(), bins, cmap=cmap, plotmissing=False,
                   units='inches', ilabel=ilabel)

    return plot.fig, df


if __name__ == '__main__':
    plotter(dict())
