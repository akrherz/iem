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
    d = dict()
    d['cache'] = 86400
    d['description'] = """Days per year with measurable precipitation. """
    d['arguments'] = [
        dict(type='networkselect', name='station', network='CSCAP',
             default='ISUAG', label='Select CSCAP Site:'),
        dict(type='select', name='model', default='echo=a1b',
             label='Select Model:', options=PDICT)
    ]
    return d


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
    clstation = nt.sts[station]['climate_site']
    (model, scenario) = ctx['model'].split("=")

    (fig, ax) = plt.subplots(1, 1)

    cursor.execute("""
    SELECT extract(year from day) as yr, sum(case when precip > 0
    THEN 1 else 0 end) from hayhoe_daily WHERE precip is not null and
    station = %s and model = %s and scenario = %s
    GROUP by yr ORDER by yr ASC
    """, (clstation, model, scenario))
    years = []
    precip = []
    for row in cursor:
        years.append(row[0])
        precip.append(row[1])

    ax.bar(years, precip, ec='b', fc='b')
    ax.grid(True)
    ax.set_ylabel("Days Per Year")
    ax.set_title("%s %s\n%s %s :: Days per Year with Measurable Precip" % (
            station, nt.sts[station]['name'], model,
            scenario))
    return fig
