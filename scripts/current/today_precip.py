"""
Generate analysis of precipitation
"""

import datetime

from pyiem.plot import MapPlot
from pyiem.reference import TRACE_VALUE
from pyiem.util import get_dbconn


def t(value):
    """Convert into something nice"""
    if value == TRACE_VALUE:
        return "T"
    return value


def main():
    """Go Main Go"""
    now = datetime.datetime.now()
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    # Compute normal from the climate database
    sql = """
    select s.id, s.network,
      ST_x(s.geom) as lon, ST_y(s.geom) as lat,
      (case when c.pday < 0 or c.day is null then 0
          else c.pday end) as rainfall
     from summary_%s c, current c2, stations s
     WHERE s.iemid = c2.iemid and c2.iemid = c.iemid and
     c2.valid > (now() - '2 hours'::interval)
     and c.day = 'TODAY'
     and s.country = 'US' and s.network ~* 'ASOS'
     and s.state in ('IA','MN','WI','IL','MO','NE','KS','SD','ND')
    """ % (now.year,)

    lats = []
    lons = []
    vals = []
    iavals = []
    valmask = []
    icursor.execute(sql)
    for row in icursor:
        lats.append(row[3])
        lons.append(row[2])
        vals.append(t(row[4]))
        iowa = row[1] == "IA_ASOS"
        valmask.append(iowa)
        if iowa:
            iavals.append(row[4])

    if len(lats) < 3:
        return

    mp = MapPlot(
        title="Iowa ASOS Rainfall Reports",
        axisbg="white",
        subtitle="%s" % (now.strftime("%d %b %Y"),),
    )
    mp.drawcounties()
    mp.plot_values(lons, lats, vals)
    pqstr = "plot c 000000000000 summary/today_prec.png bogus png"
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
