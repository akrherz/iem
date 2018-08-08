"""CSCAP Days per year with measurable precip"""

from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {
     "hadgem=a1b": "HADGEM A1B",
     "cnrm=a1b": "CNRM A1B",
     "echam5=a1b": "ECHAM5 A1B",
     "echo=a1b": "ECHO A1B",
     "pcm=a1b": "PCM A1B",
     "miroc_hi=a1b": "MIROC_HI A1B",
     "cgcm3_t47=a1b": "CGCM3_T47 A1B",
     "giss_aom=a1b": "GISS_AOM A1B",
     "hadcm3=a1b": "HADCM3 A1B",
     "cgcm3_t63=a1b": "CGCM3_T63 A1B",
    }


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """Days per year with measurable precipitation. """
    desc['arguments'] = [
        dict(type='networkselect', name='station', network='CSCAP',
             default='ISUAG', label='Select CSCAP Site:'),
        dict(type='select', name='model', default='echo=a1b',
             label='Select Model:', options=PDICT),
        dict(type='int', name='days', default=7,
             label='Number of Days'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    days = ctx['days']
    nt = NetworkTable("CSCAP")
    clstation = nt.sts[station]['climate_site']
    (model, scenario) = ctx['model'].split("=")

    (fig, ax) = plt.subplots(1, 1)

    df = read_sql("""
    WITH data as (
    SELECT day, sum(precip) OVER (ORDER by day ASC ROWS BETWEEN %s preceding
    and current row) from hayhoe_daily WHERE precip is not null and
    station = %s and model = %s and scenario = %s
    )

    SELECT extract(year from day) as yr, sum(case when
     sum < 0.01 then 1 else 0 end) as precip
     from data WHERE extract(month from day) in
     (3,4,5,6,7,8) GROUP by yr ORDER by yr ASC
    """, pgconn, params=(days - 1, clstation, model, scenario), index_col='yr')

    ax.bar(df.index.values, df['precip'].values, ec='b', fc='b')
    ax.grid(True)
    ax.set_ylabel("Days Per Year")
    ax.set_title(("%s %s\n%s %s :: Spring/Summer with No Precip over %s days"
                  ) % (station, nt.sts[station]['name'], model,
                       scenario, days))
    return fig, df


if __name__ == '__main__':
    plotter(dict())
