"""Days below threshold"""

from scipy import stats
from pandas.io.sql import read_sql
from pyiem import network
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {'above': 'At or Above Threshold',
         'below': 'Below Threshold'}
PDICT2 = {'winter': 'Winter (Dec, Jan, Feb)',
          'spring': 'Spring (Mar, Apr, May)',
          'summer': 'Summer (Jun, Jul, Aug)',
          'fall': 'Fall (Sep, Oct, Nov)',
          'all': 'Entire Year'}
PDICT3 = {'high': 'High Temperature',
          'low': 'Low Temperature',
          'precip': 'Precipitation'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """The number of days for a given season that are
    either above or below some temperature threshold."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station', network='IACLIMATE'),
        dict(type='select', name='season', default='winter',
             label='Select Season:', options=PDICT2),
        dict(type='select', name='dir', default='below',
             label='Threshold Direction:', options=PDICT),
        dict(type='select', name='var', default='low',
             label='Which Daily Variable:', options=PDICT3),
        dict(type='float', name='threshold', default=0,
             label='Temperature (F) or Precip (in) Threshold:'),
        dict(type="year", name="year", default=1893,
             label="Start Year of Plot"),

    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    season = ctx['season']
    direction = ctx['dir']
    varname = ctx['var']
    threshold = ctx['threshold']
    startyear = ctx['year']

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    b = "%s %s %s" % (varname, ">=" if direction == 'above' else '<',
                      threshold)

    df = read_sql("""
      SELECT extract(year from day + '%s month'::interval) as yr,
      sum(case when month in (12, 1, 2) and """ + b + """
      then 1 else 0 end) as winter,
      sum(case when month in (3, 4, 5) and """ + b + """
      then 1 else 0 end) as spring,
      sum(case when month in (6, 7, 8) and """ + b + """
      then 1 else 0 end) as summer,
      sum(case when month in (9, 10, 11) and """ + b + """
      then 1 else 0 end) as fall,
      sum(case when """ + b + """ then 1 else 0 end) as all
      from """ + table + """ WHERE station = %s and year >= %s
      GROUP by yr ORDER by yr ASC
    """, pgconn, params=(1 if season != 'all' else 0, station, startyear),
                  index_col='yr')
    if df.empty:
        raise ValueError("No data found for query")

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    avgv = df[season].mean()

    colorabove = 'r'
    colorbelow = 'b'
    if direction == 'below':
        colorabove = 'b'
        colorbelow = 'r'
    bars = ax.bar(df.index.values, df[season], fc=colorabove,
                  ec=colorabove, align='center')
    for i, mybar in enumerate(bars):
        if df[season].values[i] < avgv:
            mybar.set_facecolor(colorbelow)
            mybar.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color='k', zorder=2, label='Average')
    h_slope, intercept, r_value, _, _ = stats.linregress(df.index.values,
                                                         df[season])
    ax.plot(df.index.values, h_slope * df.index.values + intercept, '--',
            lw=2, color='k', label='Trend')
    ax.text(0.01, 0.99, "Avg: %.1f, slope: %.2f days/century, R$^2$=%.2f" % (
            avgv, h_slope * 100., r_value ** 2),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))
    ax.set_xlabel("Year")
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax.set_ylim(0, max([df[season].max() + df[season].max() / 7., 3]))
    ax.set_ylabel("Number of Days")
    ax.grid(True)
    msg = ("[%s] %s %.0f-%.0f Number of Days [%s] "
           "with %s %s %g%s"
           ) % (station, nt.sts[station]['name'],
                df.index.min(), df.index.max(), PDICT2[season],
                PDICT3[varname], PDICT[direction],
                threshold, r"$^\circ$F" if varname != 'precip' else 'inch')
    tokens = msg.split()
    sz = int(len(tokens) / 2)
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))
    ax.legend(ncol=1)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
