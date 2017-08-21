"""Some CSCAP Stuff"""
import psycopg2.extras
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context

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
    desc['cache'] = 86400
    desc['description'] = """Number of days per year that the two day precipitation
    total is over some threshold."""
    desc['arguments'] = [
        dict(type='networkselect', name='station', network='CSCAP',
             default='ISUAG', label='Select CSCAP Site:'),
        dict(type='select', name='model', default='echo=a1b',
             label='Select Model:', options=PDICT),
        dict(type='float', name='threshold', default='50',
             label='Precipitation Threshold (mm):'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = ctx['station']
    nt = NetworkTable("CSCAP")
    threshold = ctx['threshold']
    clstation = nt.sts[station]['climate_site']
    (model, scenario) = ctx['model'].split("=")

    (fig, ax) = plt.subplots(1, 1)

    cursor.execute("""
    WITH data as (
      SELECT day, precip, lag(precip) OVER
      (ORDER by day ASC) from hayhoe_daily
      WHERE station = %s and model = %s and
      scenario = %s and precip is not null)

    SELECT extract(year from day) as yr, sum(case when (precip+lag) >= %s
    THEN 1 else 0 end) from data GROUP by yr ORDER by yr ASC
    """, (clstation, model, scenario, threshold / 25.4))
    years = []
    precip = []
    for row in cursor:
        years.append(row[0])
        precip.append(row[1])

    ax.bar(years, precip, ec='b', fc='b')
    ax.grid(True)
    ax.set_ylabel("Days Per Year")
    ax.set_title("%s %s\n%s %s :: Two Day total over %.2f mm" % (
            station, nt.sts[station]['name'], model,
            scenario, threshold))
    return fig


if __name__ == '__main__':
    plotter(dict())
