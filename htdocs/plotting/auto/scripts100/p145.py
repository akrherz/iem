"""4 inch soil temps"""
import datetime
import calendar

import psycopg2
from pyiem import util
from pyiem.network import Table as NetworkTable
from pyiem.datatypes import temperature

XREF = {
    'AEEI4': 'A130209',
    'BOOI4': 'A130209',
    'CAMI4': 'A138019',
    'CHAI4': 'A131559',
    'CIRI4': 'A131329',
    'CNAI4': 'A131299',
    'CRFI4': 'A131909',
    'DONI4': 'A138019',
    'FRUI4': 'A135849',
    'GREI4': 'A134759',
    'KNAI4': 'A134309',
    'NASI4': 'A135879',
    'NWLI4': 'A138019',
    'OKLI4': 'A134759',
    'SBEI4': 'A138019',
    'WMNI4': 'A135849',
    'WTPI4': 'A135849'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['description'] = """This chart presents daily timeseries of 4 inch
    soil temperatures."""
    today = datetime.date.today()
    desc['arguments'] = [
        dict(type='networkselect', name='station', network='ISUSM',
             default='BOOI4', label='Select Station:'),
        dict(type='year', default=today.year, min=1988, name='year',
             label='Year to Highlight')
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
    cursor = pgconn.cursor()

    today = datetime.date.today()
    nt = NetworkTable("ISUSM")
    oldnt = NetworkTable("ISUAG")
    ctx = util.get_autoplot_context(fdict, get_description())
    station = ctx['station']
    year = ctx['year']
    _ = nt.sts[station]
    oldstation = XREF.get(station, 'A130209')

    (fig, ax) = plt.subplots()
    climo = []
    cdays = []
    cursor.execute("""
        SELECT extract(doy from valid) as d, avg(c30)
        from daily where station = %s GROUP by d ORDER by d ASC
        """, (oldstation, ))
    for row in cursor:
        climo.append(row[1])
        cdays.append(row[0])

    for yr in range(1988, today.year + 1):
        if yr in [1988, 1997]:
            continue
        x = []
        y = []
        if yr < 2014:
            units = 'F'
            cursor.execute("""
         select valid, c30
         from daily WHERE station = '%s'
         and valid >= '%s-01-01' and valid < '%s-01-01' ORDER by valid ASC
          """ % (oldstation, yr, yr+1))
        else:
            units = 'C'
            cursor.execute("""
            SELECT valid, tsoil_c_avg_qc from sm_daily WHERE
            station = '%s' and valid >='%s-01-01' and
            valid < '%s-01-01' and tsoil_c_avg_qc is not null
            ORDER by valid ASC""" % (station, yr, yr+1))
        for row in cursor:
            x.append(int(row[0].strftime("%j")) + 1)
            y.append(temperature(row[1], units).value('F'))
        color = 'skyblue'
        if yr == year:
            color = 'r'
            ax.plot(x, y, color=color, label='%s' % (year,), lw=2, zorder=3)
        else:
            ax.plot(x, y, color=color, zorder=2)

    ax.plot(cdays, climo, color='k', label='Average')

    ax.set_title(("ISU AgClimate [%s] %s \n"
                  "Site 4 inch Soil Temperature Yearly Timeseries"
                  ) % (station, nt.sts[station]['name']))
    ax.set_xlabel(("* pre-2014 data provided by [%s] %s"
                   ) % (oldstation, oldnt.sts[oldstation]['name']))
    ax.grid(True)
    ax.set_ylabel('Daily Avg Temp $^{\circ}\mathrm{F}$')
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 367)
    ax.set_ylim(-10, 90)
    ax.axhline(32, lw=2, color='purple', zorder=4)
    ax.set_yticks(range(-10, 90, 20))
    ax.legend(loc='best')

    return fig


if __name__ == '__main__':
    plotter(dict())
