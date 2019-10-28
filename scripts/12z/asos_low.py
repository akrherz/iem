"""Generate a map of the 12z UTC low temperature """
from __future__ import print_function
import datetime
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("iem", user="nobody")
    icursor = pgconn.cursor()
    now = datetime.datetime.now()

    sql = """
    WITH lows as (
     SELECT c.iemid, min(tmpf) as low12z from current_log c JOIN stations s
     ON (s.iemid = c.iemid)
     WHERE tmpf > -90 and valid > '%s 00:00:00+00' and valid < '%s 12:00:00+00'
     and s.network in ('IA_ASOS', 'AWOS') GROUP by c.iemid
    )

    select t.id, ST_x(t.geom) as lon, ST_y(t.geom) as lat, l.low12z from
    lows l JOIN stations t on (t.iemid = l.iemid)
    """ % (
        now.strftime("%Y-%m-%d"),
        now.strftime("%Y-%m-%d"),
    )

    lats = []
    lons = []
    vals = []
    valmask = []
    labels = []
    icursor.execute(sql)
    for row in icursor:
        lats.append(row[2])
        lons.append(row[1])
        vals.append(float(row[3]))
        labels.append(row[0])
        valmask.append(True)

    mp = MapPlot(
        title="Iowa ASOS/AWOS 12Z Morning Low Temperature",
        subtitle="%s" % (now.strftime("%d %b %Y"),),
        axisbg="white",
    )
    mp.drawcounties()
    mp.plot_values(lons, lats, vals, fmt="%.0f", labels=labels, labelbuffer=5)
    pqstr = (
        "plot ac %s summary/iowa_asos_12z_low.png " "iowa_asos_12z_low.png png"
    ) % (now.strftime("%Y%m%d%H%M"),)
    mp.postprocess(pqstr=pqstr)


if __name__ == "__main__":
    main()
