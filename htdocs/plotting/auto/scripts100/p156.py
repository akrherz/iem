""" Crop condition reports"""
import datetime
import calendar
from collections import OrderedDict

from pandas.io.sql import read_sql
from matplotlib.font_manager import FontProperties
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.reference import state_names
from pyiem.exceptions import NoDataFound

PDICT2 = OrderedDict([('CORN', 'Corn'),
                      ('SOYBEANS', 'Soybean')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['nass'] = True
    desc['description'] = """This chart presents crop condition reports."""
    desc['arguments'] = [
        dict(type='state', name='st1', default='IA',
             label='Select State #1:'),
        dict(type='state', name='st2', default='IL',
             label='Select State #2:'),
        dict(type='state', name='st3', default='MN',
             label='Select State #3:'),
        dict(type='state', name='st4', default='WI',
             label='Select State #4:'),
        dict(type='state', name='st5', default='MO',
             label='Select State #5:'),
        dict(type='state', name='st6', default='IN',
             label='Select State #6:'),
        dict(type='year', min=1986, name='y1',
             default=datetime.date.today().year, label='Select Year #1'),
        dict(type='year', min=1986, name='y2', optional=True,
             default=2012, label='Select Year #2'),
        dict(type='year', min=1986, name='y3', optional=True,
             default=2008, label='Select Year #3'),
        dict(type='year', min=1986, name='y4', optional=True,
             default=1993, label='Select Year #4'),
        dict(type='select', name='commodity_desc', default='CORN',
             options=PDICT2, label='Which Crop?'),

    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    st1 = ctx['st1'][:2]
    st2 = ctx['st2'][:2]
    st3 = ctx['st3'][:2]
    st4 = ctx['st4'][:2]
    st5 = ctx['st5'][:2]
    st6 = ctx['st6'][:2]
    y1 = ctx['y1']
    y2 = ctx.get('y2')
    y3 = ctx.get('y3')
    y4 = ctx.get('y4')
    years = [y1, y2, y3, y4]
    states = [st1, st2, st3, st4, st5, st6]
    commodity_desc = ctx['commodity_desc']
    df = read_sql("""
    select week_ending, state_alpha, num_value, unit_desc, year,
    extract(doy from week_ending) as doy from
    nass_quickstats
    where commodity_desc = %s  and statisticcat_desc = 'CONDITION'
    and state_alpha in %s ORDER by week_ending ASC
    """, pgconn, params=(commodity_desc, tuple(states),),
                  index_col=None)
    if df.empty:
        raise NoDataFound("ERROR: No data found!")

    prop = FontProperties(size=10)

    fig, ax = plt.subplots(3, 2, sharex=True, sharey=True, figsize=(8, 6))

    i = 0
    for row in range(3):
        for col in range(2):
            state = states[i]
            df2 = df[df['state_alpha'] == state]
            _years = df2['year'].unique()
            colors = ['black',  'green', 'blue', 'red']

            for year in _years:
                s = df2[(df2['year'] == year) &
                        ((df2['unit_desc'] == 'PCT POOR') |
                         (df2['unit_desc'] == 'PCT VERY POOR'))]
                s2 = s[['doy', 'num_value']].groupby(by=['doy']).sum()
                if year in years:
                    ax[row, col].plot(s2.index.values, s2['num_value'],
                                      c=colors.pop(),
                                      lw=3, zorder=5, label='%s' % (year,))
                else:
                    ax[row, col].plot(s2.index.values,
                                      s2['num_value'].values, c='tan')
            if row == 0 and col == 0:
                ax[row, col].legend(ncol=5, loc=(0.4, -0.19), prop=prop)
            ax[row, col].set_xticks((121, 152, 182, 213, 244, 274, 305,
                                     335, 365))
            ax[row, col].set_xticklabels(calendar.month_abbr[5:])
            ax[row, col].set_xlim(120, 310)
            ax[row, col].grid(True)
            ax[row, col].set_ylim(0, 100)
            if col == 0:
                ax[row, col].set_ylabel("Coverage [%]")
            ax[row, col].text(1., 0.5, "%s" % (state_names[state],),
                              ha='left', va='center', rotation=-90,
                              size=16, transform=ax[row, col].transAxes)
            ax[row, col].text(0.02, 0.97, state, ha='left', va='top',
                              size=14, transform=ax[row, col].transAxes)
            i += 1

    fig.text(0.5, .91, ("USDA Weekly %s Crop Condition Report (%.0f-%.0f)\n"
                        "Areal %% of State in Poor & Very Poor Condition "
                        "(thru %s)"
                        ) % (PDICT2[commodity_desc],
                             df['year'].min(), df['year'].max(),
                             df['week_ending'].max()),
             ha='center')

    return fig, df


if __name__ == '__main__':
    plotter(dict(commodity_desc='SOYBEAN', y1=2012, y2=2005, y3=1988, y4=1993))
